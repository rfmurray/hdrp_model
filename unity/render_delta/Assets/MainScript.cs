using System.IO;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.HighDefinition;
using UnityEditor;

public class MainScript : MonoBehaviour
{

    // scene objects
    public Light dirlight;          // directional light
    public Volume globalVolume;     // global volume, which we'll use to choose the cube file for tonemapping

    int frameCount = 0;             // number of frames elapsed since program started
    int frameWait = 30;             // number of frames to wait before starting rendering (burn-in period)

    int delta_m = 1;                // number of cube file currently used for tonemapping
    Texture3DParameter lutTexture;  // object that contains tonemapping table

    const float light_min = 1e-4f;         // we sweep the directional light intensity from light_min
    const float light_max = 400f;          // to light_max in multiplicative steps
    const float light_increment = 1.01f;   // of size light_increment
    float i_d;                      // current directional light intensity

    const int imsize = 4;           // size of region to capture
    Rect readRect;                  // rectangle specifying coordinates of region to capture
    Texture2D tex;                  // texture where captured region will be stored

    bool captureWaiting = false;    // flag indicating whether capture is in progress
    int captureElapsed;             // counter for frames elapsed since capture request
    int captureWait = 2;            // number of frames to wait after capture request before capturing image

    string filename = "../data_delta.txt";  // name of data file
    StreamWriter writer;                    // object to manage text file where we write the results

    void Start() {

        // get coordinates of region to capture
        int x0 = (Screen.width / 2) - (imsize / 2);
        int y0 = (Screen.height / 2) - (imsize / 2);
        readRect = new Rect(x0, y0, imsize, imsize);

        // create texture object where capture will be stored
        tex = new Texture2D(imsize, imsize, TextureFormat.RGB24, mipChain: false);

        // add post-rendering callback
        RenderPipelineManager.endCameraRendering += OnEndCameraRendering;

        // get LUT object that contains tonemapping table
        globalVolume.sharedProfile.TryGet<Tonemapping>(out var tmap);
        lutTexture = tmap.lutTexture;

        // write header to data file
        writer = new StreamWriter(filename, append: false);
        writer.WriteLine("delta_m,i_d,v_r,v_g,v_b");

    }

    void Update()
    {
        // wait for a burn-in period to elapse
        if (++frameCount < frameWait)
            return;

        // set initial stimulus properties and request a capture
        if(frameCount==frameWait)
            StimFirst();

        // keep waiting if a capture request is active
        if (captureWaiting)
            return;

        // if no longer waiting for a capture, save lighting intensity and
        // captured color coordinates to file
        Color[] v = tex.GetPixels();
        string line = $"{delta_m},{i_d:F9},{v[0].r:F6},{v[0].g:F6},{v[0].b:F6}";
        writer.WriteLine(line);

        // set next stimulus properties and request a capture
        if (!StimNext())
            Quit();

    }

    // set initial stimulus properties and request a capture
    void StimFirst()
    {
        delta_m = 1;
        SetDeltaCube();
        dirlight.intensity = i_d = light_min;
        captureWaiting = true;
        captureElapsed = 0;
    }

    // set next stimulus properties and request a capture
    bool StimNext()
    {
        i_d *= light_increment;
        if (i_d > light_max)
        {
            if (delta_m == 32)
                return false;
            ++delta_m;
            SetDeltaCube();
            i_d = light_min;
        }
        dirlight.intensity = i_d;
        captureWaiting = true;
        captureElapsed = 0;
        return true;
    }

    // load a new tonemapping table
    void SetDeltaCube()
    {
        string name = $"delta_{delta_m:D2}";
        string[] cubeguid = AssetDatabase.FindAssets(name);
        string cubepath = AssetDatabase.GUIDToAssetPath(cubeguid[0]);
        lutTexture.value = (Texture3D)AssetDatabase.LoadAssetAtPath(cubepath, typeof(Texture3D));
        Debug.Log(cubepath);
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
