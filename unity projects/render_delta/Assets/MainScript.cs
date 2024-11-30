using System.IO;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.HighDefinition;
using UnityEditor;

public class MainScript : MonoBehaviour
{

    public Light dirlight;
    public Volume globalVolume;

    int frameCount = 0, frameWait = 30;

    int delta = 3;
    Texture3DParameter lutTexture;

    const float light_increment = 1.001f;
    float i_d, light_max;

    float[] u_knot = { 0f, 1e-9f, 2.606041e-04f, 3.104486e-03f, 7.145272e-03f, 1.268643e-02f, 2.025881e-02f, 3.045015e-02f, 4.442356e-02f, 6.319271e-02f, 8.882296e-02f, 1.234868e-01f, 1.700572e-01f, 2.335635e-01f, 3.208031e-01f, 4.365856e-01f, 5.965817e-01f, 8.099239e-01f, 1.105067e+00f, 1.491640e+00f, 2.033027e+00f, 2.757723e+00f, 3.735954e+00f, 5.081779e+00f, 6.877141e+00f, 9.342603e+00f, 1.260348e+01f, 1.718516e+01f, 2.324688e+01f, 3.144579e+01f, 4.275583e+01f, 5.771645e+01f };
    float uk2id = Mathf.PI / 0.823f;

    const int imsize = 4;   // size of region to capture
    Rect readRect;          // rectangle specifying region to capture
    Texture2D tex;          // texture where captured region will be stored
    bool captureWaiting = false;
    int captureElapsed, captureWait = 2;

    string filename = "../render_delta.txt";
    StreamWriter writer;

    void Start() {

        // get coordinates of region to capture
        int x0 = (Screen.width / 2) - (imsize / 2);
        int y0 = (Screen.height / 2) - (imsize / 2);
        readRect = new Rect(x0, y0, imsize, imsize);

        // create texture object where capture will be stored
        tex = new Texture2D(imsize, imsize, TextureFormat.RGB24, mipChain: false);

        // add post-rendering callback
        RenderPipelineManager.endCameraRendering += OnEndCameraRendering;

        globalVolume.sharedProfile.TryGet<Tonemapping>(out var tmap);
        lutTexture = tmap.lutTexture;

        writer = new StreamWriter(filename, append: false);
        writer.WriteLine("delta,i_d,v_r,v_g,v_b");

    }

    void Update() {

        // skip frames during an initial period
        if (++frameCount < frameWait)
            return;

        // set initial stimulus properties and request a capture
        if(frameCount==frameWait)
            StimFirst();

        // keep waiting if a capture request is active
        if (captureWaiting)
            return;

        // save captured color coordinates to file
        Color[] v = tex.GetPixels();
        string line = $"{delta},{i_d:F9},{v[0].r:F6},{v[0].g:F6},{v[0].b:F6}";
        writer.WriteLine(line);

        // set next stimulus properties and request a capture
        if (!StimNext())
            Quit();

    }

    void StimFirst()
    {
        delta = 3;
        SetDeltaCube();
        dirlight.intensity = i_d = 0.95f * uk2id * u_knot[delta-1];
        light_max = 1.05f * uk2id * u_knot[delta];
        captureWaiting = true;
        captureElapsed = 0;
    }

    bool StimNext()
    {
        i_d *= light_increment;
        if (i_d > light_max)
        {
            if (delta == 32)
                return false;
            ++delta;
            SetDeltaCube();
            i_d = 0.95f * uk2id * u_knot[delta-2];
            light_max = 1.05f * uk2id * (delta == 32 ? u_knot[delta - 1] : u_knot[delta]);
        }
        dirlight.intensity = i_d;
        captureWaiting = true;
        captureElapsed = 0;
        return true;
    }

    void SetDeltaCube()
    {
        string name = $"delta_{delta:D2}";
        string[] cubeguid = AssetDatabase.FindAssets(name);
        string cubepath = AssetDatabase.GUIDToAssetPath(cubeguid[0]);
        lutTexture.value = (Texture3D)AssetDatabase.LoadAssetAtPath(cubepath, typeof(Texture3D));
        Debug.Log(cubepath);
    }

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
