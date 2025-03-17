using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.HighDefinition;

public class MainScript : MonoBehaviour
{
    // phases of the experiment; used to save state between calls to Update()
    enum ProgramPhase { ShowStimulus, GetResponse, Characterize }
    ProgramPhase phase = ProgramPhase.ShowStimulus;

    // public variables that appear in the Inspector view of the Main Camera object
    [Header("Check for chromatic characterization; uncheck for achromatic")]
    public bool chromaticCharacterization;  // flag whether to run chromatic or achromatic characterization
    [Header("Links to objects in the scene")]
    public GameObject stimulusObject;      // capsule object for orientation discrimination task
    public GameObject charPlane;           // large plane that will show characterization stimuli
    public Material charMaterial;          // unlit material of characterization plane
    public Volume globalVolume;            // global volume object that contains tonemapping object

    List<Color> characterizationList = new List<Color>();  // list of stimuli to show during characterization
    Tonemapping tonemap;                                   // tonemapping object

    void Start()
    {
        // seed rng from clock
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

        if (Input.GetKeyDown(KeyCode.Alpha3))  // press 3: start or stop characterization
            SetCharacterization(phase != ProgramPhase.Characterize);

        if (Input.GetKeyDown(KeyCode.Q))       // press q: quit experiment
            Quit();

        if (phase == ProgramPhase.ShowStimulus)       // show a new stimulus
            ShowNextStimulus();
        else if (phase == ProgramPhase.GetResponse)   // check for observer's keypress response to stimulus
            CheckStimulusResponse();
        else if (phase == ProgramPhase.Characterize)  // check for keypress in characterization phase
            CheckCharacterizationResponse();

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
            // normally we would record the stimulus and response information
            // in a data file at this point, but this is just a demonstration experiment
            phase = ProgramPhase.ShowStimulus;
            Debug.Log("response recorded");
        }
    }

    // ----- functions for characterization -----

    void SetCharacterization(bool on)
    {
        charPlane.SetActive(on);
        if (on)
        {
            // start characterization phase
            phase = ProgramPhase.Characterize;
            InitCharacterizationStimuli();
            ShowNextCharacterizationStimulus();
            Debug.Log("starting characterization");
        }
        else
        {
            // return to experiment phase
            phase = ProgramPhase.GetResponse;
            Debug.Log("ending characterization");
        }
    }

    void InitCharacterizationStimuli()
    {
        // create list of stimuli for characterization
        int n = 10;
        characterizationList.Clear();
        characterizationList.Add(new Color(0f, 0f, 0f));
        for (int i = 1; i <= n; i++)
        {
            float g = (float)i / (float)n;
            if (chromaticCharacterization)
            {
                characterizationList.Add(new Color(g, 0f, 0f));
                characterizationList.Add(new Color(0f, g, 0f));
                characterizationList.Add(new Color(0f, 0f, g));
            }
            characterizationList.Add(new Color(g, g, g));
        }
    }

    void CheckCharacterizationResponse()
    {
        // press space: show next characterization stimulus
        if (Input.GetKeyDown(KeyCode.Space))
        {
            if(!ShowNextCharacterizationStimulus())
            {
                SetCharacterization(false);
                Debug.Log("characterization finished");
                return;
            }
        }
    }

    bool ShowNextCharacterizationStimulus()
    {
        if (characterizationList.Count == 0)
            return false;
        charMaterial.color = characterizationList[0];
        Debug.Log($"next characterization stimulus shown: {charMaterial.color.r:F2}, {charMaterial.color.g:F2}, {charMaterial.color.b:F2}");
        characterizationList.RemoveAt(0);
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
        Debug.Log("ending experiment");
#if UNITY_EDITOR
        UnityEditor.EditorApplication.isPlaying = false;
#else
        UnityEngine.Application.Quit();
#endif
    }

}
