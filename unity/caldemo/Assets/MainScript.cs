using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.HighDefinition;

public class MainScript : MonoBehaviour
{
    // phases of the experiment; used to save state between calls to Update()
    enum ProgramPhase { ShowStimulus, GetResponse, Calibrate }
    ProgramPhase phase = ProgramPhase.ShowStimulus;

    [Header("Check for chromatic calibration; uncheck for achromatic")]
    public bool chromaticCalibration;  // flag whether to run chromatic or achromatic calibration
    [Header("Links to objects in the scene")]
    public GameObject stimulusObject;  // capsule object for orientation discrimination task
    public GameObject calPlane;        // large plane that will show calibration stimuli
    public Material calMaterial;       // unlit material of calibration plane
    public Volume globalVolume;        // global volume object that contains tonemapping object
    Tonemapping tonemap;               // tonemapping object

    List<Color> calibrationList = new List<Color>();

    void Start()
    {
        // seed rng
        int rngseed = (int)System.DateTime.Now.Ticks;
        Random.InitState(rngseed);

        // get tonemapping object
        VolumeProfile globalVolumeProfile = globalVolume.sharedProfile;
        if (globalVolumeProfile.TryGet<Tonemapping>(out var t))
            tonemap = t;
        else
            Debug.Log("unable to get tonemapping object");
    }

    void Update()
    {
        if (Input.GetKeyDown(KeyCode.Alpha1))  // turn tonemapping on
            SetTonemapping(true);

        if (Input.GetKeyDown(KeyCode.Alpha2))  // turn tonemapping off
            SetTonemapping(false);

        if (Input.GetKeyDown(KeyCode.Alpha3))  // toggle calibration
            SetCalibration(phase != ProgramPhase.Calibrate);

        if (Input.GetKeyDown(KeyCode.Q))       // quit experiment
            Quit();

        if (phase == ProgramPhase.ShowStimulus)      // show a new stimulus
            ShowNextStimulus();
        else if (phase == ProgramPhase.GetResponse)  // check for observer's keypress response to stimulus
            CheckStimulusResponse();
        else if (phase == ProgramPhase.Calibrate)    // check for keypress in calibration phase
            CheckCalibrationResponse();

    }

    // ----- functions for stimulus-response phase of experiment -----

    void ShowNextStimulus()
    {
        float theta = Random.Range(-30f, 30f);
        stimulusObject.transform.rotation = Quaternion.Euler(0f, 0f, -theta);
        phase = ProgramPhase.GetResponse;
        Debug.Log("next stimulus shown");
    }

    void CheckStimulusResponse()
    {
        if (Input.GetKeyDown(KeyCode.F) || Input.GetKeyDown(KeyCode.J))
        {
            phase = ProgramPhase.ShowStimulus;
            Debug.Log("response recorded");
        }
    }

    // ----- functions for calibration -----

    void SetCalibration(bool on)
    {
        calPlane.SetActive(on);
        if (on)
        {
            phase = ProgramPhase.Calibrate;
            InitCalibrationStimuli();
            ShowNextCalibrationStimulus();
            Debug.Log("starting calibration");
        }
        else
        {
            phase = ProgramPhase.ShowStimulus;
            Debug.Log("ending calibration");
        }
    }

    void InitCalibrationStimuli()
    {
        calibrationList.Clear();
        calibrationList.Add(new Color(0f, 0f, 0f));
        if(chromaticCalibration)
        {
            int n = 10;
            for (int i = 1; i <= n; i++)
            {
                float g = (float)i / (float)n;
                calibrationList.Add(new Color(g, 0f, 0f));
                calibrationList.Add(new Color(0f, g, 0f));
                calibrationList.Add(new Color(0f, 0f, g));
                calibrationList.Add(new Color(g, g, g));
            }
        }
        else
        {
            for (int i = 0; i <= 9; i++)
            {
                float g = (float)i / 9f;
                calibrationList.Add(new Color(g, g, g));
            }
        }
    }

    void CheckCalibrationResponse()
    {
        if (Input.GetKeyDown(KeyCode.Space))
        {
            if(!ShowNextCalibrationStimulus())
            {
                SetCalibration(false);
                Debug.Log("calibration completed");
                return;
            }
            Debug.Log("next calibration stimulus shown");
        }
    }

    bool ShowNextCalibrationStimulus()
    {
        if (calibrationList.Count == 0)
            return false;
        calMaterial.color = calibrationList[0];
        calibrationList.RemoveAt(0);
        return true;
    }

    // ----- other functions -----

    void SetTonemapping(bool on)
    {
        tonemap.mode.value = on ? TonemappingMode.External : TonemappingMode.None;
        Debug.Log("tonemapping " + (on ? "on" : "off"));
    }

    void Quit()
    {
        Debug.Log("quitting experiment");
#if UNITY_EDITOR
        UnityEditor.EditorApplication.isPlaying = false;
#else
        UnityEngine.Application.Quit();
#endif
    }

}
