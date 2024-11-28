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
    [Header("Number of random samples to render")]
    public int samples;

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
    float e;    // exposure (not randomized)

    // frame counter and trial counter
    int frameCount = 0, frameWait = 30;
    int sampleNumber = 0;
    
    const int imsize = 4;   // size of region to capture
    Rect readRect;          // rectangle specifying region to capture
    Texture2D tex;          // texture where captured region will be stored
    bool captureWaiting = false;
    int captureElapsed, captureWait = 2;
    GradientSky sky;

    StreamWriter writer;

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
        volume.sharedProfile.TryGet<GradientSky>(out GradientSky tmpSky);
        sky = tmpSky;

        // get fixed exposure level
        volume.sharedProfile.TryGet<Exposure>(out Exposure tmpExposure);
        e = tmpExposure.fixedExposure.value;

        // choose the material that we'll test
        Renderer renderer = plane.GetComponent<Renderer>();
        renderer.material = materialType == Materials.Lambertian ? materialLambertian : materialUnlit;

        // turn tonemapping on or off
        volume.sharedProfile.TryGet<Tonemapping>(out Tonemapping tonemap);
        tonemap.mode.Override(testTonemap ? TonemappingMode.External : TonemappingMode.None);

        // seed rng
        int rngseed = (int)System.DateTime.Now.Ticks;
        Random.InitState(rngseed);

        // create filename
        string filename = "../data";
        filename += materialType == Materials.Lambertian ? "_L1" : "_L0";
        filename += testTonemap ? "_T1" : "_T0";
        filename += ".txt";

        // write header to data file
        writer = new StreamWriter(filename, append: false);
        writer.WriteLine("sampleNumber,e,m_r,m_g,m_b,n_x,n_y,n_z,l_x,l_y,l_z,i_d,d_r,d_g,d_b,i_a,a_r,a_g,a_b,v_r,v_g,v_b");
    }

    void Update()
    {
        // skip frames during an initial period
        if (++frameCount < 30)
            return;

        // set random stimulus properties and request first capture
        if (frameCount == frameWait)
            StimNext();

        // keep waiting if a request is active
        if (captureWaiting)
            return;

        // save scene parameters and captured color coordinates to file
        Color[] v = tex.GetPixels();                // 'tex' was captured in the OnEndCameraRendering callback
        string line = $"{sampleNumber}";            // sample number
        line += $",{e:F6}";                         // exposure
        line += $",{m.r:F6},{m.g:F6},{m.b:F6}";     // material color
        line += $",{n.x:F6},{n.y:F6},{n.z:F6}";     // plane surface normal
        line += $",{l.x:F6},{l.y:F6},{l.z:F6}";           // directional light direction
        line += $",{i_d:F6},{d.r:F6},{d.g:F6},{d.b:F6}";  // directional light intensity and color
        line += $",{i_a:F6},{a.r:F6},{a.g:F6},{a.b:F6}";  // ambient light intensity and color
        line += $",{v[0].r:F6},{v[0].g:F6},{v[0].b:F6}";  // post-processed rendered color
        writer.WriteLine(line);

        // set random stimulus properties and request next capture
        if (!StimNext())
            Quit();

    }

    Color RandomColor()
    {
        return new Color(Random.Range(0f, 1f), Random.Range(0f, 1f), Random.Range(0f, 1f));
    }

    Vector3 RandomUnitVector3(float maxDeclination = 60f)
    {
        float azimuth = Random.Range(0f, 2 * Mathf.PI);
        float declination = Random.Range(0f, (maxDeclination / 180f) * Mathf.PI);
        return new Vector3(Mathf.Sin(declination) * Mathf.Cos(azimuth),
                           Mathf.Sin(declination) * Mathf.Sin(azimuth),
                           -Mathf.Cos(declination));
    }

    bool StimNext()
    {
        // if we have enough samples, then quit
        if (++sampleNumber > samples)
            return false;

        // choose random stimulus properties
        m = RandomColor();        // plane color
        n = RandomUnitVector3();  // plane normal vector
        d = RandomColor();        // directional light color
        l = RandomUnitVector3();  // directional light direction
        a = RandomColor();        // ambient light color
        i_d = Random.Range(0f, Mathf.PI * 3f) * Mathf.Pow(2f, e);  // directional light intensity; scale with exposure so we get reasonable rendered values
        i_a = Random.Range(0f, 3f) * Mathf.Pow(2f, e);             // ambient light intensity

        // assign stimulus properties to objects

        // plane color and orientation
        if (materialType == Materials.Lambertian)
            materialLambertian.SetColor("_BASE_COLOR", m);
        else
            materialUnlit.color = m;
        plane.transform.rotation = Quaternion.FromToRotation(new Vector3(0f, 1f, 0f), n);  // default plane normal is (0, 1, 0)

        // directional light color, intensity, and direction
        directionalLight.color = d;
        directionalLight.intensity = i_d;
        directionalLight.transform.rotation = Quaternion.FromToRotation(new Vector3(0f, 0f, -1f), l);  // default lighting direction is (0, 0, -1)

        // ambient light color and intensity
        sky.top.value = sky.middle.value = sky.bottom.value = a;
        sky.multiplier.value = i_a;

        // start a capture request        
        captureWaiting = true;
        captureElapsed = 0;

        return true;
    }

    void OnEndCameraRendering(ScriptableRenderContext context, Camera camera)
    {
        if (camera != Camera.main)  // don't capture pixels if this is the wrong camera
            return;

        if (!captureWaiting)  // don't capture pixels if there isn't an active request
            return;

        if (++captureElapsed < captureWait)  // don't capture pixels until we've waited a few frames after the request
            return;

        // copy pixels from framebuffer into texture
        tex.ReadPixels(readRect, 0, 0, recalculateMipMaps: false);
        captureWaiting = false;
    }

    void OnDestroy()
    {
        RenderPipelineManager.endCameraRendering -= OnEndCameraRendering;
    }

    void Quit()
    {
        writer.Close();
#if UNITY_EDITOR
        // quit when running project in editor
        UnityEditor.EditorApplication.isPlaying = false;
#else
        // quit when running compiled project
        UnityEngine.Application.Quit();
#endif
    }

}
