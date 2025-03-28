using System.IO;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.HighDefinition;

public class MainScript : MonoBehaviour
{

    // user-configurable rendering parameters
    [Header("Check to render Lambertian material; uncheck for Unlit")]
    public bool testLambertian;                // flag whether to render Lambertian (true) or unlit (false) material
    [Header("Check to apply tonemapping")]
    public bool testTonemap;                   // flag whether to apply tonemapping
    [Header("Number of random samples to render")]
    public int samples;                        // number of samples to capture
    [Header("Lighting scale factor")]
    public float lightingScale;                // scale factor for lighting, to take into account exposure setting

    // scene objects
    [Header("Links to scene objects")]
    public GameObject plane;
    public Material materialLambertian, materialUnlit;
    public Light directionalLight;
    public Volume volume;

    // scene and object properties that we'll randomize
    // - same variable names as in the paper
    Color m;    // material color
    Vector3 n;  // plane surface normal
    Color d;    // directional light color
    Vector3 l;  // directional light direction
    float i_d;  // directional light intensity
    Color a;    // ambient light color
    float i_a;  // ambient light intensity
    float e;    // exposure (not randomized)

    int frameCount = 0;           // number of frames elapsed since program started
    int frameWait = 30;           // number of frames to wait before starting rendering (burn-in period)

    int sampleNumber = 0;         // number of sample currently being rendered
    bool captureWaiting = false;  // flag indicating whether capture is in progress
    int captureElapsed;           // counter for frames elapsed since capture request
    int captureWait = 2;          // number of frames to wait after capture request before capturing image
    const int imsize = 4;         // size of region to capture
    Rect readRect;                // rectangle specifying coordinates of region to capture
    Texture2D tex;                // texture where captured region will be stored

    GradientSky sky;              // object used to set ambient lighting properties

    StreamWriter writer;          // object to manage text file where we write the results

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

        // get exposure object
        volume.sharedProfile.TryGet<Exposure>(out Exposure tmpExposure);
        e = tmpExposure.fixedExposure.value;

        // choose which material type we'll render
        Renderer renderer = plane.GetComponent<Renderer>();
        renderer.material = testLambertian ? materialLambertian : materialUnlit;

        // turn tonemapping on or off
        volume.sharedProfile.TryGet<Tonemapping>(out Tonemapping tonemap);
        tonemap.mode.Override(testTonemap ? TonemappingMode.External : TonemappingMode.None);

        // seed rng from clock
        int rngseed = (int)System.DateTime.Now.Ticks;
        Random.InitState(rngseed);

        // create filename
        // - filenames have this pattern: ../data_L1_T1_identity.txt
        // - material type is indicated by L0 (unlit) or L1 (Lambertian)
        // - tonemapping status is indicated by T0 (off) or T1 (on)
        // - if tonemapping is on, the last part of the filename is the cube filename, such as "identity"
        string cubename;
        if (testTonemap)
        {
            cubename = tonemap.lutTexture.ToString();
            int k = cubename.IndexOf("(UnityEngine");
            cubename = "_" + cubename.Substring(0, k - 1);
        }
        else
            cubename = "";
        string filename = $"../data_L{(testLambertian ? 1 : 0)}_T{(testTonemap ? 1 : 0)}{cubename}.txt";

        // write header to data file
        writer = new StreamWriter(filename, append: false);
        writer.WriteLine("sampleNumber,e,m_r,m_g,m_b,n_x,n_y,n_z,l_x,l_y,l_z,i_d,d_r,d_g,d_b,i_a,a_r,a_g,a_b,v_r,v_g,v_b");
    }

    void Update()
    {
        // wait for a burn-in period to elapse
        if (++frameCount < 30)
            return;

        // set random stimulus properties and request capture
        if (frameCount == frameWait)
            StimNext();

        // keep waiting if a request is active
        if (captureWaiting)
            return;

        // if no longer waiting for a capture, then save scene parameters
        // and captured color coordinates to file
        Color[] v = tex.GetPixels();                      // 'tex' was captured in the OnEndCameraRendering callback
        string line = $"{sampleNumber}";                  // sample number
        line += $",{e:F6}";                               // exposure
        line += $",{m.r:F6},{m.g:F6},{m.b:F6}";           // material color
        line += $",{n.x:F6},{n.y:F6},{n.z:F6}";           // plane surface normal
        line += $",{l.x:F6},{l.y:F6},{l.z:F6}";           // directional light direction
        line += $",{i_d:F6},{d.r:F6},{d.g:F6},{d.b:F6}";  // directional light intensity and color
        line += $",{i_a:F6},{a.r:F6},{a.g:F6},{a.b:F6}";  // ambient light intensity and color
        line += $",{v[0].r:F6},{v[0].g:F6},{v[0].b:F6}";  // post-processed rendered color
        writer.WriteLine(line);

        // set random stimulus properties and request next capture
        if (!StimNext())
            Quit();

    }

    // get a random color
    Color RandomColor()
    {
        return new Color(Random.Range(0f, 1f), Random.Range(0f, 1f), Random.Range(0f, 1f));
    }

    // get a random unit vector
    Vector3 RandomUnitVector3(float maxDeclination = 60f)
    {
        // use inverse transform sampling to get uniformly distributed points on the sphere
        float azimuth = Random.Range(0f, 2f * Mathf.PI);
        float declination = Mathf.Acos(1 + Random.Range(0f, 1f) * (Mathf.Cos((Mathf.PI / 180f) * maxDeclination) - 1));
        return new Vector3(Mathf.Sin(declination) * Mathf.Cos(azimuth),
                           Mathf.Sin(declination) * Mathf.Sin(azimuth),
                           -Mathf.Cos(declination));
    }

    // assign random stimulus properties and request capture
    bool StimNext()
    {
        // if we have enough samples, then quit
        if (++sampleNumber > samples)
            return false;

        // choose random stimulus properties
        m = RandomColor();           // plane color
        n = RandomUnitVector3();     // plane normal vector
        d = RandomColor();           // directional light color
        l = RandomUnitVector3();     // directional light direction
        a = RandomColor();           // ambient light color
        i_d = lightingScale * Random.Range(0f, Mathf.PI * 2f) * Mathf.Pow(2f, e);  // directional light intensity; scale with exposure so we get reasonable rendered values
        i_a = lightingScale * Random.Range(0f, 2f) * Mathf.Pow(2f, e);             // ambient light intensity

        // assign stimulus properties to objects

        // plane color and orientation
        if (testLambertian)
            materialLambertian.SetColor("_BASE_COLOR", m);
        else
            materialUnlit.color = m;
        plane.transform.rotation = Quaternion.FromToRotation(new Vector3(0f, 1f, 0f), n);  // default plane normal is (0, 1, 0)

        // directional light color, intensity, and direction
        directionalLight.color = d;
        directionalLight.intensity = i_d;
        directionalLight.transform.rotation = Quaternion.FromToRotation(new Vector3(0f, 0f, -1f), l);  // default lighting direction is (0, 0, -1) (here we require l indicates the direction light is coming from, not the direction it's going to)

        // ambient light color and intensity
        sky.top.value = sky.middle.value = sky.bottom.value = a;
        sky.multiplier.value = i_a;

        // start a capture request        
        captureWaiting = true;
        captureElapsed = 0;

        // periodically show number of samples captured so far
        if (sampleNumber % 100 == 0)
            Debug.Log($"{sampleNumber} / {samples}");

        return true;
    }

    // callback that captures rendered pixels
    void OnEndCameraRendering(ScriptableRenderContext context, Camera camera)
    {
        if (camera != Camera.main)  // don't capture pixels if this is the wrong camera
            return;

        if (!captureWaiting)        // don't capture pixels if there isn't an active request
            return;

        if (++captureElapsed < captureWait)  // don't capture pixels until we've waited a few frames after the request
            return;

        // copy pixels from framebuffer into texture
        tex.ReadPixels(readRect, 0, 0, recalculateMipMaps: false);
        captureWaiting = false;
    }

    // when shutting down, remove callback
    void OnDestroy()
    {
        RenderPipelineManager.endCameraRendering -= OnEndCameraRendering;
    }

    // end program
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
