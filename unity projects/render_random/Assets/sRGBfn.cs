using UnityEngine;

public class sRGBfn
{

    private const float Phi = 12.9232102f, Gamma = 2.4f, A = 0.055f, X = 0.039285f, Y = 0.0030399f;

    public static float sRGB(float x)
    {
        return x < X ? x / Phi : Mathf.Pow((x + A) / (1 + A), Gamma);
    }

    public static Color sRGB(Color c)
    {
        return new Color(sRGB(c.r), sRGB(c.g), sRGB(c.b));
    }

    public static float sRGBinv(float y)
    {
        return y < Y ? y * Phi : Mathf.Pow(y, 1 / Gamma) * (1 + A) - A;
    }

    public static Color sRGBinv(Color c)
    {
        return new Color(sRGBinv(c.r), sRGBinv(c.g), sRGBinv(c.b));
    }

}
