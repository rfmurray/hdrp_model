using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.HighDefinition;
using UnityEditor;

public class MainScript : MonoBehaviour
{

    public Light dirlight;

    public Volume globalVolume;
    Texture3DParameter texparam;
    int delta = 1, phase = 0, framei = 0;

    const float light_min = 1e-4f, light_max = 400f, light_increment = 1.01f;
    float light_intensity;

    float plane_grey_out = -1f;

    StreamWriter sr;

    WaitForEndOfFrame frameEnd = new WaitForEndOfFrame();
    int startx, starty;

    void Start() {

        startx = Screen.width / 2;
        starty = Screen.height / 2;

        globalVolume.sharedProfile.TryGet<Tonemapping>(out var tmap);
        texparam = tmap.lutTexture;

        sr = System.IO.File.CreateText("../render_delta.txt");
        sr.WriteLine("delta,light_intensity,grey_out");

    }

    void Update() {

        framei += 1;

        // initial wait
        if (phase == 0)
        {
            if (framei < 5)
                return;

            phase = 1;
            light_intensity = light_min;
            framei = 0;
            StartCoroutine(Capture());  // need this?
            SetDelta();
            return;
        }

        // set stimulus property  [ maybe don't need a separate phase? ]
        if (phase == 1)
        {
            if (framei < 1)
                return;

            dirlight.intensity = light_intensity;
            phase = 2;
            framei = 0;
            return;
        }

        // start capture of rendered grey level
        if (phase == 2)
        {
            if (framei < 1)
                return;

            StartCoroutine(Capture());
            phase = 3;
            framei = 0;
            return;
        }

        // get rendered grey level
        if (phase == 3)
        {
            if (framei < 1)
                return;

            string dataline = $"{delta},{light_intensity:F9},{plane_grey_out}"; // record red, green, and blue color coordinates
            sr.WriteLine(dataline);

            light_intensity *= light_increment;
            if (light_intensity > light_max)
            {
                if (++delta > 32)
                    Finish();
                else
                {
                    SetDelta();
                    light_intensity = light_min;
                }
            }
            phase = 1;
            framei = 0;
            return;
        }

    }

    void SetDelta()
    {
        string name = $"delta_{delta:D2}";
        string[] cubeguid = AssetDatabase.FindAssets(name);
        string cubepath = AssetDatabase.GUIDToAssetPath(cubeguid[0]);
        texparam.value = (Texture3D)AssetDatabase.LoadAssetAtPath(cubepath, typeof(Texture3D));
        Debug.Log(cubepath);
    }

    void Finish()
    {
        sr.Close();
        UnityEditor.EditorApplication.isPlaying = false;
    }

    // record greylevel
    IEnumerator Capture()
    {
        // wait until rendering of a single frame is done
        yield return frameEnd;

        // record greylevel
        var tex = new Texture2D(1, 1, TextureFormat.RGB24, false); // reuse this?
        tex.ReadPixels(new Rect(startx, starty, 1, 1), 0, 0);
        tex.Apply();
        var pix = tex.GetPixels32();  // process this as floating point
        Destroy(tex);
        plane_grey_out = (pix[0].r + pix[0].g + pix[0].b) / 3;
    }

}
