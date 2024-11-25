using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.HighDefinition;

public class MainScript : MonoBehaviour
{

    // user-configurable rendering parameters
    public enum Materials { Lambertian, Unlit }
    [Header("Choose material type to render")]
    public Materials materialType;
    [Header("Check to apply tonemapping")]
    public bool testTonemap;
    [Header("Check to use a fixed pseudo-random sequence")]
    public bool fixedSeed;
    [Header("Check to randomize wider range of properties")]
    public bool randomizeAll;
    [Header("Number of random samples to render")]
    public int samples;
    [Header("Maximum rendered value u_k (Lambertian only)")]
    public float max_uk;

    // scene objects
    [Header("Links to scene objects")]
    public GameObject plane;
    public Material materialLambertian, materialUnlit;
    public Light directionalLight;
    public Volume volume;

    // properties of scene objects that we'll set randomly
    // - here I use the same variable names as in the paper
    // - this makes them less readable at first, but in the long run makes
    //   it easier to map them onto the content of the paper
    Color m;    // material color
    Vector3 n;  // plane surface normal
    Color d;    // directional light color
    Vector3 l;  // directional light direction
    float i_d;  // directional light intensity
    Color a;    // ambient light color
    float i_a;  // ambient light intensity

    // frame counter and trial counter
    int frameCount = 0, sampleNumber = 0;
    
    const int imsize = 4;   // size of region to capture
    Rect readRect;          // rectangle specifying region to capture
    Texture2D tex;          // texture where captured region will be stored
    bool captureRequested = false, captureWaiting = false;
    int captureElapsed, captureWait = 2;
    GradientSky sky;

    string filename;

    void Start()
    {
        // get coordinates of region to capture
        int x0 = (Screen.width / 2) - (imsize / 2);
        int y0 = (Screen.height / 2) - (imsize / 2);
        readRect = new Rect(x0, y0, imsize, imsize);

        // create texture object where capture will be stored
        tex = new Texture2D(imsize, imsize, TextureFormat.RGB24, mipChain: false);

        // add post-rendering callback
        RenderPipelineManager.endCameraRendering += OnEndCameraRendering;

        // get gradient sky object
        volume.sharedProfile.TryGet<GradientSky>(out GradientSky tmpsky);
        sky = tmpsky;

        // choose the material that we'll test
        Renderer renderer = plane.GetComponent<Renderer>();
        renderer.material = materialType == Materials.Lambertian ? materialLambertian : materialUnlit;

        // turn tonemapping on or off
        volume.sharedProfile.TryGet<Tonemapping>(out Tonemapping tonemap);
        tonemap.mode.Override(testTonemap ? TonemappingMode.External : TonemappingMode.None);

        // seed rng
        int rngseed = fixedSeed ? 0 : (int)System.DateTime.Now.Ticks;
        Random.InitState(rngseed);

        // create filename
        filename = "../data";
        filename += materialType == Materials.Lambertian ? "_L1" : "_L0";
        filename += testTonemap ? "_T1" : "_T0";
        filename += fixedSeed ? "_F1" : "_F0";
        filename += randomizeAll ? "_A1" : "_A0";
        filename += $"_S{samples:D5}";
        filename += $"_M{max_uk:F0}";
        filename += ".txt";

        // write header to data file
        using (StreamWriter writer = new StreamWriter(filename, append: false))
            writer.WriteLine("sampleNumber,m_r,m_g,m_b,n_x,n_y,n_z,l_x,l_y,l_z,i_d,d_r,d_g,d_b,i_a,a_r,a_g,a_b,v_r,v_g,v_b");
    }

    void Update()
    {
        // skip frames during an initial period
        if (++frameCount < 30)
            return;

        if (captureRequested)
        {
            if (captureWaiting)
                return;

            // convert captured region to Color values
            Color[] v = tex.GetPixels();

            // save results to file
            string line = $"{sampleNumber}";            // sample number
            line += $",{m.r:F6},{m.g:F6},{m.b:F6}";     // material color
            line += $",{n.x:F6},{n.y:F6},{n.z:F6}";     // plane surface normal
            line += $",{l.x:F6},{l.y:F6},{l.z:F6}";           // directional light direction
            line += $",{i_d:F6},{d.r:F6},{d.g:F6},{d.b:F6}";  // directional light intensity and color
            line += $",{i_a:F6},{a.r:F6},{a.g:F6},{a.b:F6}";  // ambient light intensity and color
            line += $",{v[0].r:F6},{v[0].g:F6},{v[0].b:F6}";  // post-processed rendered color
            using (StreamWriter writer = new StreamWriter(filename, append: true))
                writer.WriteLine(line);

            captureWaiting = false;

            if (sampleNumber == samples)
                Quit();
        }

        // choose random stimulus properties

        // plane color and normal vector
        m = new Color(Random.Range(0f, 1f), Random.Range(0f, 1f), Random.Range(0f, 1f));
        n = RandomUnitVector3();

        // directional light color and direction
        d = new Color(Random.Range(0f, 1f), Random.Range(0f, 1f), Random.Range(0f, 1f));
        l = RandomUnitVector3();

        // ambient light color
        a = new Color(Random.Range(0f, 1f), Random.Range(0f, 1f), Random.Range(0f, 1f));

        // choose light intensities so that the largest rendered color
        // coordinate u_k has a target value, randomly chosen on [0, max_uk]
        float target_uk = Random.Range(0f, max_uk);
        float proportion_directional = Random.Range(0f, 1f);
        float illum = target_uk / (0.822f * Mathf.Max(m.r, m.g, m.b));
        float illum_d = proportion_directional * illum;
        float illum_a = (1 - proportion_directional) * illum;
        float d_max = Mathf.Max(d.r, d.g, d.b);
        float a_max = Mathf.Max(a.r, a.g, a.b);
        float costheta = Vector3.Dot(n, l);
        i_d = illum_d / ( sRGBfn.sRGB(d_max) * Mathf.Max(costheta, 0) / Mathf.PI );
        i_a = illum_a / a_max;
        //float lighti = target_uk / (2f * 0.822f);
        //i_d = Random.Range(0f, Mathf.PI * lighti);
        //i_a = Random.Range(0f, lighti);

        // assign stimulus properties to objects

        // plane color and orientation
        if (materialType == Materials.Lambertian)
            materialLambertian.SetColor("_BASE_COLOR", m);
        else
            materialUnlit.color = m;
        plane.transform.rotation = Quaternion.FromToRotation(new Vector3(0f, 1f, 0f), n);

        // directional light color, intensity, and direction
        directionalLight.color = d;
        directionalLight.intensity = i_d;
        directionalLight.transform.rotation = Quaternion.FromToRotation(new Vector3(0f, 0f, -1f), l);
        // using Quaternion.FromToRotation(), we can assign the lighting direction
        // using the direction vector l instead of Euler angles; the default
        // lighting direction is (0, 0, -1), so we find the rotation that maps
        // that to l.

        // ambient light color and intensity
        sky.top.value = sky.middle.value = sky.bottom.value = a;
        sky.multiplier.value = i_a;

        // start a capture request        
        ++sampleNumber;
        captureRequested = captureWaiting = true;
        captureElapsed = 0;
    }

    Vector3 RandomUnitVector3()
    {
        float azimuth = Random.Range(0f, 2 * Mathf.PI);
        float declination = Random.Range(-(60f / 180f) * Mathf.PI, (60f / 180f) * Mathf.PI);
        return new Vector3(Mathf.Sin(declination)*Mathf.Cos(azimuth),
                           Mathf.Sin(declination) * Mathf.Sin(azimuth),
                           -Mathf.Cos(declination));
    }

    void OnEndCameraRendering(ScriptableRenderContext context, Camera camera)
    {
        if (camera != Camera.main)  // don't capture pixels if this is the wrong camera
            return;

        if (!(captureRequested && captureWaiting))  // don't capture pixels if there isn't an active request
            return;

        if (++captureElapsed < captureWait)  // don't capture pixels until we've waited a few frames after the request
            return;

        // copy pixels from framebuffer into texture
        tex.ReadPixels(readRect, 0, 0, recalculateMipMaps: false);
        captureWaiting = false;
    }

    float colormax(Color c)
    {
        return Mathf.Max(c.r, c.g, c.b);
    }

    void OnDestroy()
    {
        RenderPipelineManager.endCameraRendering -= OnEndCameraRendering;
    }

    void Quit()
    {
#if UNITY_EDITOR
        // quit when running project in editor
        UnityEditor.EditorApplication.isPlaying = false;
#else
        // quit when running compiled project
        UnityEngine.Application.Quit();
#endif
    }

}
