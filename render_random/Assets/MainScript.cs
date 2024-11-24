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
    public int max_uk;

    // scene objects
    [Header("Links to scene objects")]
    public GameObject plane;
    public Material materialLambertian, materialUnlit;
    public Light directionalLight;
    public Volume volume;

    // properties of scene objects that we'll set randomly
    Color materialColor, directionalColor, ambientColor;
    Vector3 planeNormal, lightDir;
    float directionalIntensity, ambientMultiplier;

    // frame counter and trial counter
    int frameCount = 0, trialCount = 0;
    
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
            writer.WriteLine("trialCount,planeColorR,planeColorG,planeColorB,planeNormalX,planeNormalY,planeNormalZ,lightDirX,lightDirY,lightDirZ,directionalIntensity,directionalColorR,directionalColorG,directionalColorB,ambientMultiplier,ambientColorR,ambientColorG,ambientColorB,renderR,renderG,renderB");
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
            Color[] pix = tex.GetPixels();

            // save results to file
            string line = $"{trialCount}";
            line += $",{materialColor.r:F6},{materialColor.g:F6},{materialColor.b:F6}";
            line += $",{planeNormal.x:F6},{planeNormal.y:F6},{planeNormal.z:F6}";
            line += $",{lightDir.x:F6},{lightDir.y:F6},{lightDir.z:F6}";
            line += $",{directionalIntensity:F6},{directionalColor.r:F6},{directionalColor.g:F6},{directionalColor.b:F6}";
            line += $",{ambientMultiplier:F6},{ambientColor.r:F6},{ambientColor.g:F6},{ambientColor.b:F6}";
            line += $",{pix[0].r:F6},{pix[0].g:F6},{pix[0].b:F6}";
            using (StreamWriter writer = new StreamWriter(filename, append: true))
                writer.WriteLine(line);

            captureWaiting = false;

            if (trialCount == samples)
                Quit();
        }

        // set new stimulus properties

        // plane color and orientation
        materialColor = new Color(Random.Range(0f, 1f), Random.Range(0f, 1f), Random.Range(0f, 1f));
        if (materialType == Materials.Lambertian)
            materialLambertian.SetColor("_BASE_COLOR", materialColor);
        else
            materialUnlit.color = materialColor;
        planeNormal = RandomUnitVector3();
        plane.transform.rotation = Quaternion.FromToRotation(new Vector3(0f, 1f, 0f), planeNormal);

        // directional light color, intensity, and direction
        directionalColor = new Color(Random.Range(0f, 1f), Random.Range(0f, 1f), Random.Range(0f, 1f));
        directionalLight.color = directionalColor;
        directionalLight.intensity = directionalIntensity = Random.Range(0f, Mathf.PI * 1.2f);
        lightDir = RandomUnitVector3();
        directionalLight.transform.rotation = Quaternion.FromToRotation(new Vector3(0f, 0f, -1f), lightDir);

        // ambient light color and intensity
        ambientColor = new Color(Random.Range(0f, 1f), Random.Range(0f, 1f), Random.Range(0f, 1f));
        sky.top.value = sky.middle.value = sky.bottom.value = ambientColor;
        sky.multiplier.value = ambientMultiplier = Random.Range(0f, 1.2f);

        // start a capture request        
        ++trialCount;
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
