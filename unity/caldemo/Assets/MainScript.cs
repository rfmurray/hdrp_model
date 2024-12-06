using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.HighDefinition;

public class MainScript : MonoBehaviour
{
    // phases of the experiment; used to save state between calls to Update()
    enum ProgramPhase { ShowStimulus, GetResponse, Calibrate }
    ProgramPhase phase = ProgramPhase.ShowStimulus;

    // public variables that appear in the Inspector view of the Main Camera object
    [Header("Check for chromatic calibration; uncheck for achromatic")]
    public bool chromaticCalibration;  // flag whether to run chromatic or achromatic calibration
    [Header("Links to objects in the scene")]
    public GameObject stimulusObject;  // capsule object for orientation discrimination task
    public GameObject calPlane;        // large plane that will show calibration stimuli
    public Material calMaterial;       // unlit material of calibration plane
    public Volume globalVolume;        // global volume object that contains tonemapping object

    List<Color> calibrationList = new List<Color>();  // list of stimuli to show during calibration
    Tonemapping tonemap;                              // tonemapping object

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
        if (Input.GetKeyDown(KeyCode.Alpha1))  // press 1: turn tonemapping on
            SetTonemapping(true);

        if (Input.GetKeyDown(KeyCode.Alpha2))  // press 2: turn tonemapping off
            SetTonemapping(false);

        if (Input.GetKeyDown(KeyCode.Alpha3))  // press 3: start or stop calibration
            SetCalibration(phase != ProgramPhase.Calibrate);

        if (Input.GetKeyDown(KeyCode.Q))       // press q: quit experiment
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
        // rotate capsule object to a random orientation
        float theta = Random.Range(-30f, 30f);
        stimulusObject.transform.rotation = Quaternion.Euler(0f, 0f, -theta);
        phase = ProgramPhase.GetResponse;
        Debug.Log("next stimulus shown");
    }

    void CheckStimulusResponse()
    {
        // f = counterclockwise, j = clockwise
        if (Input.GetKeyDown(KeyCode.F) || Input.GetKeyDown(KeyCode.J))
        {
            // normally we would record the stimulus and response here,
            // but this is just a demonstration experiment
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
            // start calibraiton phase
            phase = ProgramPhase.Calibrate;
            InitCalibrationStimuli();
            ShowNextCalibrationStimulus();
            Debug.Log("starting calibration");
        }
        else
        {
            // return to experiment phase
            phase = ProgramPhase.ShowStimulus;
            Debug.Log("ending calibration");
        }
    }

    void InitCalibrationStimuli()
    {
        // create list of stimuli for calibration
        int n = 10;
        calibrationList.Clear();
        calibrationList.Add(new Color(0f, 0f, 0f));
        for (int i = 1; i <= n; i++)
        {
            float g = (float)i / (float)n;
            if (chromaticCalibration)
            {
                calibrationList.Add(new Color(g, 0f, 0f));
                calibrationList.Add(new Color(0f, g, 0f));
                calibrationList.Add(new Color(0f, 0f, g));
            }
            calibrationList.Add(new Color(g, g, g));
        }
    }

    void CheckCalibrationResponse()
    {
        // press space: show next calibration stimulus
        if (Input.GetKeyDown(KeyCode.Space))
        {
            if(!ShowNextCalibrationStimulus())
            {
                SetCalibration(false);
                Debug.Log("calibration finished");
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
