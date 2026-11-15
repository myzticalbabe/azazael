// LumenRefresh - standalone clone of the ASUS Lumina OLED "pixel refresh" screensaver.
//
// The footage is the real vendor routine lifted from this machine
// (%LOCALAPPDATA%\Temp\OLED_ScreenSaver_2024_v2_Ending_Logo.wmv, 3840x2160 24fps),
// trimmed to its 60s loopable body and re-encoded with ffmpeg into the embedded asset.
// The embedded copy is 720p (17.7 MB, 23% below the 1080p one) purely to keep the exe
// small - the app scales it up. For full-resolution deliverables render with
// --source smoke_1080.mp4 instead.
//
// Everything after decode is ours: colour grading, pattern effects, OLED pixel shift.
//
// Build:  csc /target:winexe /platform:x64 /optimize+ /unsafe+ /out:LumenRefresh.exe
//             LumenRefresh.cs /resource:smoke_720.mp4,smoke.mp4
//             /r:System.Windows.Forms.dll /r:System.Drawing.dll
//
// Run:    LumenRefresh.exe --palette ember --speed 0.85
//         LumenRefresh.exe --list-palettes
//         LumenRefresh.exe --selftest
//         LumenRefresh.exe --dump out\ --palette teal --times 5,25,50

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Imaging;
using System.Globalization;
using System.IO;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;
using System.Windows.Forms;
using Microsoft.Win32;

namespace LumenRefresh
{
    // ---------------------------------------------------------------- Media Foundation

    internal static class MF
    {
        public const int MF_VERSION = 0x00020070;
        public const int MFSTARTUP_FULL = 0;
        public const int MF_SOURCE_READER_FIRST_VIDEO_STREAM = unchecked((int)0xFFFFFFFC);
        public const int MF_SOURCE_READERF_ENDOFSTREAM = 0x00000002;
        public const int MF_SOURCE_READERF_STREAMTICK = 0x00000100;

        public static readonly Guid MF_MT_MAJOR_TYPE = new Guid("48eba18e-f8c9-4687-bf11-0a74c9f96a8f");
        public static readonly Guid MF_MT_SUBTYPE = new Guid("f7e34c9a-42e8-4714-b74b-cb29d72c35e5");
        public static readonly Guid MF_MT_FRAME_SIZE = new Guid("1652c33d-d6b2-4012-b834-72030849a37d");
        public static readonly Guid MF_MT_DEFAULT_STRIDE = new Guid("644b4e48-1e02-4516-b0eb-c01ca9d49ac6");
        public static readonly Guid MFMediaType_Video = new Guid("73646976-0000-0010-8000-00AA00389B71");
        public static readonly Guid MFVideoFormat_RGB32 = new Guid("00000016-0000-0010-8000-00AA00389B71");
        public static readonly Guid MF_SOURCE_READER_ENABLE_VIDEO_PROCESSING =
            new Guid("fb394f3d-ccf1-42ee-bbb3-f9b845d5681d");

        [DllImport("mfplat.dll", ExactSpelling = true)]
        public static extern int MFStartup(int version, int dwFlags);

        [DllImport("mfplat.dll", ExactSpelling = true)]
        public static extern int MFShutdown();

        [DllImport("mfplat.dll", ExactSpelling = true)]
        public static extern int MFCreateAttributes(out IMFAttributes ppMFAttributes, int cInitialSize);

        [DllImport("mfplat.dll", ExactSpelling = true)]
        public static extern int MFCreateMediaType(out IMFMediaType ppMFType);

        [DllImport("mfreadwrite.dll", ExactSpelling = true, CharSet = CharSet.Unicode)]
        public static extern int MFCreateSourceReaderFromURL(string pwszURL, IMFAttributes pAttributes,
                                                            out IMFSourceReader ppSourceReader);
    }

    [StructLayout(LayoutKind.Explicit, Size = 24)]
    internal struct PropVariant
    {
        [FieldOffset(0)] public short vt;
        [FieldOffset(8)] public long hVal;
    }

    [ComImport, Guid("2CD2D921-C447-44A7-A13C-4ADABFC247E3"),
     InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    internal interface IMFAttributes
    {
        [PreserveSig] int GetItem(ref Guid guidKey, IntPtr pValue);
        [PreserveSig] int GetItemType(ref Guid guidKey, out int pType);
        [PreserveSig] int CompareItem(ref Guid guidKey, IntPtr value, out int pbResult);
        [PreserveSig] int Compare(IntPtr pTheirs, int matchType, out int pbResult);
        [PreserveSig] int GetUINT32(ref Guid guidKey, out uint punValue);
        [PreserveSig] int GetUINT64(ref Guid guidKey, out ulong punValue);
        [PreserveSig] int GetDouble(ref Guid guidKey, out double pfValue);
        [PreserveSig] int GetGUID(ref Guid guidKey, out Guid pguidValue);
        [PreserveSig] int GetStringLength(ref Guid guidKey, out uint pcchLength);
        [PreserveSig] int GetString(ref Guid guidKey, IntPtr pwszValue, uint cchBufSize, out uint pcchLength);
        [PreserveSig] int GetAllocatedString(ref Guid guidKey, out IntPtr ppwszValue, out uint pcchLength);
        [PreserveSig] int GetBlobSize(ref Guid guidKey, out uint pcbBlobSize);
        [PreserveSig] int GetBlob(ref Guid guidKey, IntPtr pBuf, uint cbBufSize, out uint pcbBlobSize);
        [PreserveSig] int GetAllocatedBlob(ref Guid guidKey, out IntPtr ppBuf, out uint pcbSize);
        [PreserveSig] int GetUnknown(ref Guid guidKey, ref Guid riid, out IntPtr ppv);
        [PreserveSig] int SetItem(ref Guid guidKey, IntPtr value);
        [PreserveSig] int DeleteItem(ref Guid guidKey);
        [PreserveSig] int DeleteAllItems();
        [PreserveSig] int SetUINT32(ref Guid guidKey, uint unValue);
        [PreserveSig] int SetUINT64(ref Guid guidKey, ulong unValue);
        [PreserveSig] int SetDouble(ref Guid guidKey, double fValue);
        [PreserveSig] int SetGUID(ref Guid guidKey, ref Guid guidValue);
        [PreserveSig] int SetString(ref Guid guidKey, [MarshalAs(UnmanagedType.LPWStr)] string wszValue);
        [PreserveSig] int SetBlob(ref Guid guidKey, byte[] pBuf, uint cbBufSize);
        [PreserveSig] int SetUnknown(ref Guid guidKey, IntPtr pUnknown);
        [PreserveSig] int LockStore();
        [PreserveSig] int UnlockStore();
        [PreserveSig] int GetCount(out uint pcItems);
        [PreserveSig] int GetItemByIndex(uint unIndex, out Guid pguidKey, IntPtr pValue);
        [PreserveSig] int CopyAllItems(IntPtr pDest);
    }

    // The IMFAttributes methods are repeated in full in each derived interface instead of using
    // C# interface inheritance: the CLR does not lay inherited COM vtable slots out the way the
    // native interfaces do, so calls to derived members landed on the wrong slot and crashed.

    [ComImport, Guid("44AE0FA8-EA31-4109-8D2E-4CAE4997C555"),
     InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    internal interface IMFMediaType
    {
        // ---- IMFAttributes, flattened
        [PreserveSig] int GetItem(ref Guid guidKey, IntPtr pValue);
        [PreserveSig] int GetItemType(ref Guid guidKey, out int pType);
        [PreserveSig] int CompareItem(ref Guid guidKey, IntPtr value, out int pbResult);
        [PreserveSig] int Compare(IntPtr pTheirs, int matchType, out int pbResult);
        [PreserveSig] int GetUINT32(ref Guid guidKey, out uint punValue);
        [PreserveSig] int GetUINT64(ref Guid guidKey, out ulong punValue);
        [PreserveSig] int GetDouble(ref Guid guidKey, out double pfValue);
        [PreserveSig] int GetGUID(ref Guid guidKey, out Guid pguidValue);
        [PreserveSig] int GetStringLength(ref Guid guidKey, out uint pcchLength);
        [PreserveSig] int GetString(ref Guid guidKey, IntPtr pwszValue, uint cchBufSize, out uint pcchLength);
        [PreserveSig] int GetAllocatedString(ref Guid guidKey, out IntPtr ppwszValue, out uint pcchLength);
        [PreserveSig] int GetBlobSize(ref Guid guidKey, out uint pcbBlobSize);
        [PreserveSig] int GetBlob(ref Guid guidKey, IntPtr pBuf, uint cbBufSize, out uint pcbBlobSize);
        [PreserveSig] int GetAllocatedBlob(ref Guid guidKey, out IntPtr ppBuf, out uint pcbSize);
        [PreserveSig] int GetUnknown(ref Guid guidKey, ref Guid riid, out IntPtr ppv);
        [PreserveSig] int SetItem(ref Guid guidKey, IntPtr value);
        [PreserveSig] int DeleteItem(ref Guid guidKey);
        [PreserveSig] int DeleteAllItems();
        [PreserveSig] int SetUINT32(ref Guid guidKey, uint unValue);
        [PreserveSig] int SetUINT64(ref Guid guidKey, ulong unValue);
        [PreserveSig] int SetDouble(ref Guid guidKey, double fValue);
        [PreserveSig] int SetGUID(ref Guid guidKey, ref Guid guidValue);
        [PreserveSig] int SetString(ref Guid guidKey, [MarshalAs(UnmanagedType.LPWStr)] string wszValue);
        [PreserveSig] int SetBlob(ref Guid guidKey, byte[] pBuf, uint cbBufSize);
        [PreserveSig] int SetUnknown(ref Guid guidKey, IntPtr pUnknown);
        [PreserveSig] int LockStore();
        [PreserveSig] int UnlockStore();
        [PreserveSig] int GetCount(out uint pcItems);
        [PreserveSig] int GetItemByIndex(uint unIndex, out Guid pguidKey, IntPtr pValue);
        [PreserveSig] int CopyAllItems(IntPtr pDest);

        // ---- IMFMediaType
        [PreserveSig] int GetMajorType(out Guid pguidMajorType);
        [PreserveSig] int IsCompressedFormat(out int pfCompressed);
        [PreserveSig] int IsEqual(IMFMediaType pIMediaType, out uint pdwFlags);
        [PreserveSig] int GetRepresentation(ref Guid guidRepresentation, out IntPtr ppvRepresentation);
        [PreserveSig] int FreeRepresentation(ref Guid guidRepresentation, IntPtr pvRepresentation);
    }

    [ComImport, Guid("045FA593-8799-42B8-BC8D-8968C6453507"),
     InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    internal interface IMFMediaBuffer
    {
        [PreserveSig] int Lock(out IntPtr ppbBuffer, out int pcbMaxLength, out int pcbCurrentLength);
        [PreserveSig] int Unlock();
        [PreserveSig] int GetCurrentLength(out int pcbCurrentLength);
        [PreserveSig] int SetCurrentLength(int cbCurrentLength);
        [PreserveSig] int GetMaxLength(out int pcbMaxLength);
    }

    [ComImport, Guid("C40A00F2-B93A-4D80-AE8C-5A1C634F58E4"),
     InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    internal interface IMFSample
    {
        // ---- IMFAttributes, flattened
        [PreserveSig] int GetItem(ref Guid guidKey, IntPtr pValue);
        [PreserveSig] int GetItemType(ref Guid guidKey, out int pType);
        [PreserveSig] int CompareItem(ref Guid guidKey, IntPtr value, out int pbResult);
        [PreserveSig] int Compare(IntPtr pTheirs, int matchType, out int pbResult);
        [PreserveSig] int GetUINT32(ref Guid guidKey, out uint punValue);
        [PreserveSig] int GetUINT64(ref Guid guidKey, out ulong punValue);
        [PreserveSig] int GetDouble(ref Guid guidKey, out double pfValue);
        [PreserveSig] int GetGUID(ref Guid guidKey, out Guid pguidValue);
        [PreserveSig] int GetStringLength(ref Guid guidKey, out uint pcchLength);
        [PreserveSig] int GetString(ref Guid guidKey, IntPtr pwszValue, uint cchBufSize, out uint pcchLength);
        [PreserveSig] int GetAllocatedString(ref Guid guidKey, out IntPtr ppwszValue, out uint pcchLength);
        [PreserveSig] int GetBlobSize(ref Guid guidKey, out uint pcbBlobSize);
        [PreserveSig] int GetBlob(ref Guid guidKey, IntPtr pBuf, uint cbBufSize, out uint pcbBlobSize);
        [PreserveSig] int GetAllocatedBlob(ref Guid guidKey, out IntPtr ppBuf, out uint pcbSize);
        [PreserveSig] int GetUnknown(ref Guid guidKey, ref Guid riid, out IntPtr ppv);
        [PreserveSig] int SetItem(ref Guid guidKey, IntPtr value);
        [PreserveSig] int DeleteItem(ref Guid guidKey);
        [PreserveSig] int DeleteAllItems();
        [PreserveSig] int SetUINT32(ref Guid guidKey, uint unValue);
        [PreserveSig] int SetUINT64(ref Guid guidKey, ulong unValue);
        [PreserveSig] int SetDouble(ref Guid guidKey, double fValue);
        [PreserveSig] int SetGUID(ref Guid guidKey, ref Guid guidValue);
        [PreserveSig] int SetString(ref Guid guidKey, [MarshalAs(UnmanagedType.LPWStr)] string wszValue);
        [PreserveSig] int SetBlob(ref Guid guidKey, byte[] pBuf, uint cbBufSize);
        [PreserveSig] int SetUnknown(ref Guid guidKey, IntPtr pUnknown);
        [PreserveSig] int LockStore();
        [PreserveSig] int UnlockStore();
        [PreserveSig] int GetCount(out uint pcItems);
        [PreserveSig] int GetItemByIndex(uint unIndex, out Guid pguidKey, IntPtr pValue);
        [PreserveSig] int CopyAllItems(IntPtr pDest);

        // ---- IMFSample
        [PreserveSig] int GetSampleFlags(out int pdwSampleFlags);
        [PreserveSig] int SetSampleFlags(int dwSampleFlags);
        [PreserveSig] int GetSampleTime(out long phnsSampleTime);
        [PreserveSig] int SetSampleTime(long hnsSampleTime);
        [PreserveSig] int GetSampleDuration(out long phnsSampleDuration);
        [PreserveSig] int SetSampleDuration(long hnsSampleDuration);
        [PreserveSig] int GetBufferCount(out int pdwBufferCount);
        [PreserveSig] int GetBufferByIndex(int dwIndex, out IMFMediaBuffer ppBuffer);
        [PreserveSig] int ConvertToContiguousBuffer(out IMFMediaBuffer ppBuffer);
        [PreserveSig] int AddBuffer(IMFMediaBuffer pBuffer);
        [PreserveSig] int RemoveBufferByIndex(int dwIndex);
        [PreserveSig] int RemoveAllBuffers();
        [PreserveSig] int GetTotalLength(out int pcbTotalLength);
        [PreserveSig] int CopyToBuffer(IMFMediaBuffer pBuffer);
    }

    [ComImport, Guid("70AE66F2-C809-4E4F-8915-BDCB406B7993"),
     InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    internal interface IMFSourceReader
    {
        [PreserveSig] int GetStreamSelection(int dwStreamIndex, out int pfSelected);
        [PreserveSig] int SetStreamSelection(int dwStreamIndex, int fSelected);
        [PreserveSig] int GetNativeMediaType(int dwStreamIndex, int dwMediaTypeIndex, out IMFMediaType ppMediaType);
        [PreserveSig] int GetCurrentMediaType(int dwStreamIndex, out IMFMediaType ppMediaType);
        [PreserveSig] int SetCurrentMediaType(int dwStreamIndex, IntPtr pdwReserved, IMFMediaType pMediaType);
        [PreserveSig] int SetCurrentPosition(ref Guid guidTimeFormat, ref PropVariant varPosition);
        [PreserveSig] int ReadSample(int dwStreamIndex, int dwControlFlags, out int pdwActualStreamIndex,
                                     out int pdwStreamFlags, out long pllTimestamp, out IntPtr ppSample);
        [PreserveSig] int Flush(int dwStreamIndex);
        [PreserveSig] int GetServiceForStream(int dwStreamIndex, ref Guid guidService, ref Guid riid, out IntPtr ppvObject);
        [PreserveSig] int GetPresentationAttribute(int dwStreamIndex, ref Guid guidAttribute, out PropVariant pvarAttribute);
    }

    // ---------------------------------------------------------------- Grade

    /// <summary>A colour transform: hue/saturation matrix, per-channel gain, gamma and an optional luminance ramp.</summary>
    internal sealed class Grade
    {
        public string Name = "native";
        public float GainR = 1f, GainG = 1f, GainB = 1f;
        public float Saturation = 1f;
        public float HueDegrees = 0f;
        public float Contrast = 1f;
        public float Lift = 0f;
        public float Gamma = 1f;
        public float Mix = 1f;            // 0 = untouched footage, 1 = fully graded
        public Color[] Ramp;              // when set, luminance is mapped through this ramp
        public float PulseAmount = 0f;    // 0..1 breathing brightness
        public float PulseHz = 0.08f;

        // Two-ink duotone: the footage has two dyes, so give each its own colour instead
        // of rotating both by the same hue. The selector is derived from the source's
        // blue-minus-green, which separates these particular inks cleanly.
        public bool HasDuo;
        public Color DuoA = Color.Black, DuoB = Color.Black;

        // Refresh dose control: 0 = off, else the mean luminance to normalise to (0..1),
        // so every palette delivers a comparable amount of light to the panel.
        public float TargetLuma = 0f;

        // derived
        internal int[] _m = new int[9];
        internal byte[] _lutR, _lutG, _lutB;
        internal int[] _rampR, _rampG, _rampB;
        internal int[] _duoAR, _duoAG, _duoAB, _duoBR, _duoBG, _duoBB;
        // B - A per channel. The duotone is a straight line in the selector, so the
        // pixel loop only needs A plus one multiply instead of two tables and a divide.
        internal int[] _duoDR, _duoDG, _duoDB;
        internal int _mix256 = 256;
        internal int _luma256 = 256;

        public static readonly Dictionary<string, string> Presets = new Dictionary<string, string>
        {
            { "native",  "" },
            { "ember",   "hue=-18 sat=1.45 gain=1.35,1.0,0.62 contrast=1.12" },
            { "magma",   "hue=-32 sat=1.7 gain=1.5,0.8,0.45 contrast=1.2" },
            { "teal",    "hue=142 sat=1.5 gain=0.7,1.25,1.35 contrast=1.1" },
            { "ice",     "hue=170 sat=1.15 gain=0.8,1.05,1.45 contrast=1.08" },
            { "violet",  "hue=-72 sat=1.6 gain=1.15,0.75,1.45 contrast=1.12" },
            { "lime",    "hue=95 sat=1.7 gain=0.85,1.45,0.6 contrast=1.1" },
            { "ruby",    "hue=8 sat=1.6 gain=1.45,0.65,0.7 contrast=1.15" },
            { "amber",   "hue=-28 sat=1.3 gain=1.4,1.05,0.5 contrast=1.1" },
            { "mono",    "sat=0 contrast=1.18 gain=1.15,1.15,1.15" },
            { "thermal", "ramp=#000814,#003566,#ffc300,#ff6b00,#ffffff" },
            { "ash",     "ramp=#0a0a0a,#6d6d6d,#e8e8e8" },
            { "venom",   "ramp=#000000,#0b2e13,#39ff14,#eaffea" },
            { "neon",    "ramp=#05000a,#3a0ca3,#f72585,#4cc9f0,#ffffff" },
            { "prism",   "hue=0 sat=1.3" },

            // true two-ink duotones: each dye gets its own colour, so the bloom keeps
            // both inks distinct instead of rotating them onto one hue
            { "duo-cyan",   "duo=#ff6b00,#00e5ff" },
            { "duo-violet", "duo=#ffd166,#7b2cbf" },
            { "duo-blood",  "duo=#ff2d2d,#00ffa3" },
            { "duo-sun",    "duo=#ffd400,#1b3fb8" },

            // extra ramps for range
            { "solaris", "ramp=#0b0500,#5c1a00,#ff8a00,#ffe066,#fffdf5" },
            { "deepsea", "ramp=#000308,#03243b,#0a7f8f,#79f2d0,#f2fffb" },
            { "toxic",   "ramp=#020600,#123d0a,#79ff3d,#eaffb0" },
            { "rose",    "ramp=#0a0002,#3d0518,#ff2f6e,#ffc2d4,#fff5f8" },

            // NEON: near-black grounds with one screaming accent, so the plumes read as
            // signage rather than smoke.
            { "neon-cyan", "ramp=#00040a,#00303f,#00e5ff,#b9f6ff,#ffffff" },
            { "neon-pink", "ramp=#0a0010,#3d0033,#ff00a0,#ff8ae0,#fff0fa" },
            { "neon-lime", "ramp=#000a00,#0b3300,#39ff14,#c6ff8a,#f7fff0" },

            // FLUORESCENT: acid-bright, blown highlights, the ink pushed past what the
            // source actually contains.
            { "fluoro-sun",    "hue=-22 sat=2.1 gain=1.55,1.4,0.3 contrast=1.3 lift=0.06" },
            { "fluoro-mint",   "hue=150 sat=2.0 gain=0.45,1.65,1.25 contrast=1.25 lift=0.07" },
            { "fluoro-violet", "hue=-100 sat=2.1 gain=1.05,0.45,1.7 contrast=1.28 lift=0.06" },

            // PASTEL: washed and lifted, low contrast, but with enough chroma left that the
            // two inks stay apart.
            { "pastel",      "sat=0.55 gain=1.05 lift=0.16 contrast=0.85" },
            { "pastel-mint", "hue=150 sat=0.5 gain=0.95,1.1,1.05 lift=0.18 contrast=0.82" },
            { "pastel-rose", "hue=-40 sat=0.55 gain=1.1,0.93,1.0 lift=0.18 contrast=0.82" },

            // ELECTRICS: indigo ground, periwinkle sheath, hard cyan arc, white core.
            { "electric",    "ramp=#00020a,#1a00cc,#4d5cff,#00eaff,#ffffff" },
            { "elec-violet", "ramp=#06000f,#3a00c8,#a02bff,#e9ccff,#ffffff" },

            // SUNSET CLOUDS: coral and lavender, the way lit cloud banks actually stack.
            { "sunset",        "ramp=#14002b,#5c1a4a,#c2410c,#ff9e64,#ffe7c2" },
            { "sunset-clouds", "duo=#ff9e64,#8f6bd8" },

            // YOUTUBE BLUE: the light UI blue (#3EA6FF) and the deep brand blue (#065FD4).
            { "yt-blue", "ramp=#00060f,#0b2c4d,#3ea6ff,#cfeaff,#ffffff" },
            { "yt-deep", "ramp=#000208,#00204d,#065fd4,#6ea8ff,#eaf4ff" },
        };

        public static Grade FromName(string name)
        {
            Grade g = new Grade();
            g.Name = name;
            string spec;
            if (Presets.TryGetValue(name, out spec)) g.ApplySpec(spec);
            else g.ApplySpec(name);            // allow "--palette hue=90,sat=2" inline
            return g;
        }

        /// <summary>Parses "hue=-18 sat=1.45 gain=1.35,1.0,0.62" style strings.</summary>
        public void ApplySpec(string spec)
        {
            if (string.IsNullOrEmpty(spec)) return;
            string[] parts = spec.Split(new[] { ' ' }, StringSplitOptions.RemoveEmptyEntries);
            for (int i = 0; i < parts.Length; i++)
            {
                string p = parts[i];
                int eq = p.IndexOf('=');
                if (eq < 0) continue;
                string k = p.Substring(0, eq).ToLowerInvariant();
                string v = p.Substring(eq + 1);
                switch (k)
                {
                    case "hue": HueDegrees = F(v); break;
                    case "sat": Saturation = F(v); break;
                    case "contrast": Contrast = F(v); break;
                    case "lift": Lift = F(v); break;
                    case "gamma": Gamma = F(v); break;
                    case "mix": Mix = F(v); break;
                    case "pulse": PulseAmount = F(v); break;
                    case "pulsehz": PulseHz = F(v); break;
                    case "gain":
                        string[] gs = v.Split(',');
                        if (gs.Length >= 3) { GainR = F(gs[0]); GainG = F(gs[1]); GainB = F(gs[2]); }
                        else if (gs.Length == 1) { GainR = GainG = GainB = F(gs[0]); }
                        break;
                    case "ramp":
                        string[] hexes = v.Split(',');
                        List<Color> cs = new List<Color>();
                        for (int c = 0; c < hexes.Length; c++) cs.Add(ParseHex(hexes[c]));
                        if (cs.Count >= 2) Ramp = cs.ToArray();
                        break;
                    case "luma": TargetLuma = F(v); break;
                    case "duo":
                        string[] ds = v.Split(',');
                        if (ds.Length >= 2)
                        {
                            DuoA = ParseHex(ds[0]);
                            DuoB = ParseHex(ds[1]);
                            HasDuo = true;
                            Ramp = null;      // duotone and a single ramp are alternatives
                        }
                        break;
                }
            }
        }

        private static float F(string s)
        {
            float r;
            float.TryParse(s, NumberStyles.Float, CultureInfo.InvariantCulture, out r);
            return r;
        }

        private static Color ParseHex(string s)
        {
            s = s.Trim().TrimStart('#');
            if (s.Length == 3)
                s = new string(new[] { s[0], s[0], s[1], s[1], s[2], s[2] });
            if (s.Length != 6) return Color.Black;
            int v = int.Parse(s, NumberStyles.HexNumber, CultureInfo.InvariantCulture);
            return Color.FromArgb((v >> 16) & 255, (v >> 8) & 255, v & 255);
        }

        /// <summary>Bakes the grade into integer LUTs so the per-pixel loop stays cheap.</summary>
        public void Compile()
        {
            // hue rotation H, then saturation S around luma; the pixel path uses S*H.
            double h = HueDegrees * Math.PI / 180.0;
            double cosA = Math.Cos(h), sinA = Math.Sin(h);
            double[,] H = new double[3, 3];
            H[0, 0] = 0.213 + cosA * 0.787 - sinA * 0.213;
            H[0, 1] = 0.715 - cosA * 0.715 - sinA * 0.715;
            H[0, 2] = 0.072 - cosA * 0.072 + sinA * 0.928;
            H[1, 0] = 0.213 - cosA * 0.213 + sinA * 0.143;
            H[1, 1] = 0.715 + cosA * 0.285 + sinA * 0.140;
            H[1, 2] = 0.072 - cosA * 0.072 - sinA * 0.283;
            H[2, 0] = 0.213 - cosA * 0.213 - sinA * 0.787;
            H[2, 1] = 0.715 - cosA * 0.715 + sinA * 0.715;
            H[2, 2] = 0.072 + cosA * 0.928 + sinA * 0.072;

            double[] w = new double[] { 0.213, 0.715, 0.072 };
            double sat = Saturation;
            // out = luma + (in - luma) * sat   ->   M[r,c] = w[c]*(1-sat) + (r==c ? sat : 0)
            double[,] S = new double[3, 3];
            for (int r = 0; r < 3; r++)
                for (int c = 0; c < 3; c++)
                    S[r, c] = w[c] * (1.0 - sat) + (r == c ? sat : 0.0);

            for (int r = 0; r < 3; r++)
            {
                for (int c = 0; c < 3; c++)
                {
                    double sum = 0;
                    for (int k = 0; k < 3; k++) sum += S[r, k] * H[k, c];
                    _m[r * 3 + c] = (int)Math.Round(sum * 256.0);
                }
            }

            _lutR = ChannelLut(GainR, Lift, Gamma, Contrast, 0);
            _lutG = ChannelLut(GainG, Lift, Gamma, Contrast, 1);
            _lutB = ChannelLut(GainB, Lift, Gamma, Contrast, 2);

            if (Ramp != null && Ramp.Length >= 2)
            {
                _rampR = new int[256]; _rampG = new int[256]; _rampB = new int[256];
                int n = Ramp.Length - 1;
                for (int i = 0; i < 256; i++)
                {
                    double t = i / 255.0 * n;
                    int idx = (int)t;
                    if (idx > n - 1) idx = n - 1;
                    double f = t - idx;
                    Color a = Ramp[idx], b = Ramp[idx + 1];
                    _rampR[i] = (int)Math.Round(a.R + (b.R - a.R) * f);
                    _rampG[i] = (int)Math.Round(a.G + (b.G - a.G) * f);
                    _rampB[i] = (int)Math.Round(a.B + (b.B - a.B) * f);
                }
            }
            if (HasDuo)
            {
                _duoAR = new int[256]; _duoAG = new int[256]; _duoAB = new int[256];
                _duoBR = new int[256]; _duoBG = new int[256]; _duoBB = new int[256];
                BuildDuoRamp(DuoA, _duoAR, _duoAG, _duoAB);
                BuildDuoRamp(DuoB, _duoBR, _duoBG, _duoBB);
                RebuildDuoDelta();
            }

            _mix256 = (int)Math.Round(Math.Max(0, Math.Min(1, Mix)) * 256);

            // Dose normalisation needs the grade's own mid-grey luminance, so it runs last,
            // against the arrays just built.
            _luma256 = 256;
            if (TargetLuma > 0.01f)
            {
                int rr, gg, bb;
                SampleCore(128, 128, 128, out rr, out gg, out bb);
                double lum = (0.213 * rr + 0.715 * gg + 0.072 * bb) / 255.0;
                if (lum > 0.005)
                {
                    double f = TargetLuma / lum;
                    if (f < 0.05) f = 0.05;
                    if (f > 6.0) f = 6.0;
                    _luma256 = (int)Math.Round(f * 256.0);
                }
            }
        }

        private void RebuildDuoDelta()
        {
            _duoDR = new int[256]; _duoDG = new int[256]; _duoDB = new int[256];
            for (int i = 0; i < 256; i++)
            {
                _duoDR[i] = _duoBR[i] - _duoAR[i];
                _duoDG[i] = _duoBG[i] - _duoAG[i];
                _duoDB[i] = _duoBB[i] - _duoAB[i];
            }
        }

        /// <summary>Exact integer v/255 for v in [0, 65535].</summary>
        internal static int Div255(int v) { return (v + 1 + (v >> 8)) >> 8; }

        /// <summary>Black -> ink -> pale tint. Keeping the ink's own shading is what makes
        /// the two dyes still read as liquids rather than flat posterisation.</summary>
        private static void BuildDuoRamp(Color ink, int[] pr, int[] pg, int[] pb)
        {
            Color hi = Color.FromArgb(
                ink.R + (255 - ink.R) * 3 / 4,
                ink.G + (255 - ink.G) * 3 / 4,
                ink.B + (255 - ink.B) * 3 / 4);
            for (int i = 0; i < 256; i++)
            {
                double t = i / 255.0;
                if (t < 0.72)
                {
                    double f = t / 0.72;
                    pr[i] = (int)Math.Round(ink.R * f);
                    pg[i] = (int)Math.Round(ink.G * f);
                    pb[i] = (int)Math.Round(ink.B * f);
                }
                else
                {
                    double f = (t - 0.72) / 0.28;
                    pr[i] = (int)Math.Round(ink.R + (hi.R - ink.R) * f);
                    pg[i] = (int)Math.Round(ink.G + (hi.G - ink.G) * f);
                    pb[i] = (int)Math.Round(ink.B + (hi.B - ink.B) * f);
                }
            }
        }

        /// <summary>
        /// Grade one pixel without the dose/pulse/mix tail. Shared by Map (stills, selftest)
        /// so the offline and on-screen paths cannot drift apart.
        /// </summary>
        internal void SampleCore(int r, int g, int b, out int outR, out int outG, out int outB)
        {
            int nr = (_m[0] * r + _m[1] * g + _m[2] * b) >> 8;
            int ng = (_m[3] * r + _m[4] * g + _m[5] * b) >> 8;
            int nb = (_m[6] * r + _m[7] * g + _m[8] * b) >> 8;
            if (nr < 0) nr = 0; else if (nr > 255) nr = 255;
            if (ng < 0) ng = 0; else if (ng > 255) ng = 255;
            if (nb < 0) nb = 0; else if (nb > 255) nb = 255;
            nr = _lutR[nr]; ng = _lutG[ng]; nb = _lutB[nb];

            if (HasDuo)
            {
                int y = (nr * 77 + ng * 150 + nb * 29) >> 8;
                int sel = 128 + (((b - g) * 410) >> 9);
                sel &= ~(sel >> 31);
                int ds = sel - 255; sel -= ds & ~(ds >> 31);
                outR = _duoAR[y] + ((_duoDR[y] * sel) >> 8);
                outG = _duoAG[y] + ((_duoDG[y] * sel) >> 8);
                outB = _duoAB[y] + ((_duoDB[y] * sel) >> 8);
            }
            else if (_rampR != null)
            {
                int y = (nr * 77 + ng * 150 + nb * 29) >> 8;
                outR = _rampR[y]; outG = _rampG[y]; outB = _rampB[y];
            }
            else { outR = nr; outG = ng; outB = nb; }
        }

        private static byte[] ChannelLut(float gain, float lift, float gamma, float contrast, int ch)
        {
            byte[] lut = new byte[256];
            double g = gamma <= 0.01 ? 1.0 : gamma;
            for (int i = 0; i < 256; i++)
            {
                double v = i / 255.0;
                v = v * gain + lift;
                v = (v - 0.5) * contrast + 0.5;
                if (v < 0) v = 0;
                if (v > 1) v = 1;
                v = Math.Pow(v, 1.0 / g);
                lut[i] = (byte)Math.Round(v * 255.0);
            }
            return lut;
        }

        /// <summary>Colour of a grade applied to a single RGB triple - used by selftest and dumps.</summary>
        public Color Map(int r, int g, int b, float pulse)
        {
            int outR, outG, outB;
            SampleCore(r, g, b, out outR, out outG, out outB);
            if (_luma256 != 256)
            {
                outR = (outR * _luma256) >> 8; outG = (outG * _luma256) >> 8; outB = (outB * _luma256) >> 8;
                if (outR > 255) outR = 255; if (outG > 255) outG = 255; if (outB > 255) outB = 255;
            }
            if (pulse != 1f)
            {
                outR = (int)(outR * pulse); outG = (int)(outG * pulse); outB = (int)(outB * pulse);
                if (outR > 255) outR = 255; if (outG > 255) outG = 255; if (outB > 255) outB = 255;
            }
            int m = _mix256;
            outR = (outR * m + r * (256 - m)) >> 8;
            outG = (outG * m + g * (256 - m)) >> 8;
            outB = (outB * m + b * (256 - m)) >> 8;
            return Color.FromArgb(outR, outG, outB);
        }

        internal Grade Clone()
        {
            Grade g = (Grade)MemberwiseClone();
            g._m = (int[])_m.Clone();
            g._lutR = (byte[])_lutR.Clone(); g._lutG = (byte[])_lutG.Clone(); g._lutB = (byte[])_lutB.Clone();
            if (_rampR != null)
            {
                g._rampR = (int[])_rampR.Clone(); g._rampG = (int[])_rampG.Clone(); g._rampB = (int[])_rampB.Clone();
            }
            if (_duoAR != null)
            {
                g._duoAR = (int[])_duoAR.Clone(); g._duoAG = (int[])_duoAG.Clone(); g._duoAB = (int[])_duoAB.Clone();
                g._duoBR = (int[])_duoBR.Clone(); g._duoBG = (int[])_duoBG.Clone(); g._duoBB = (int[])_duoBB.Clone();
                g._duoDR = (int[])_duoDR.Clone(); g._duoDG = (int[])_duoDG.Clone(); g._duoDB = (int[])_duoDB.Clone();
            }
            return g;
        }

        /// <summary>
        /// A copy of <paramref name="a"/> whose baked colour tables are linearly mixed
        /// toward <paramref name="b"/>. Blending the compiled tables rather than the specs
        /// keeps the per-pixel cost identical to a single static grade.
        /// </summary>
        internal static Grade Blend(Grade a, Grade b, float t)
        {
            Grade g = a.Clone();
            if (t <= 0f) return g;
            if (t >= 1f) t = 1f;
            for (int i = 0; i < 256; i++)
            {
                g._lutR[i] = LerpB(a._lutR[i], b._lutR[i], t);
                g._lutG[i] = LerpB(a._lutG[i], b._lutG[i], t);
                g._lutB[i] = LerpB(a._lutB[i], b._lutB[i], t);
            }
            for (int i = 0; i < 9; i++) g._m[i] = (int)Math.Round(a._m[i] + (b._m[i] - a._m[i]) * t);

            // Ramp and duo grades are both "colour = f(luminance, selector)", so a pair of
            // them - in any combination - can be mixed exactly: a ramp is a duo whose two
            // dyes are equal. Mixing only the ramp tables, as this used to do, silently
            // returned grade A whenever the other side was a duo palette.
            bool aExp = a._rampR != null || a._duoAR != null;
            bool bExp = b._rampR != null || b._duoAR != null;
            if (aExp && bExp)
            {
                int[] aLoR = a._duoAR != null ? a._duoAR : a._rampR;
                int[] aLoG = a._duoAR != null ? a._duoAG : a._rampG;
                int[] aLoB = a._duoAR != null ? a._duoAB : a._rampB;
                int[] aHiR = a._duoAR != null ? a._duoBR : a._rampR;
                int[] aHiG = a._duoAR != null ? a._duoBG : a._rampG;
                int[] aHiB = a._duoAR != null ? a._duoBB : a._rampB;
                int[] bLoR = b._duoAR != null ? b._duoAR : b._rampR;
                int[] bLoG = b._duoAR != null ? b._duoAG : b._rampG;
                int[] bLoB = b._duoAR != null ? b._duoAB : b._rampB;
                int[] bHiR = b._duoAR != null ? b._duoBR : b._rampR;
                int[] bHiG = b._duoAR != null ? b._duoBG : b._rampG;
                int[] bHiB = b._duoAR != null ? b._duoBB : b._rampB;

                g._duoAR = new int[256]; g._duoAG = new int[256]; g._duoAB = new int[256];
                g._duoBR = new int[256]; g._duoBG = new int[256]; g._duoBB = new int[256];
                for (int i = 0; i < 256; i++)
                {
                    g._duoAR[i] = LerpI(aLoR[i], bLoR[i], t);
                    g._duoAG[i] = LerpI(aLoG[i], bLoG[i], t);
                    g._duoAB[i] = LerpI(aLoB[i], bLoB[i], t);
                    g._duoBR[i] = LerpI(aHiR[i], bHiR[i], t);
                    g._duoBG[i] = LerpI(aHiG[i], bHiG[i], t);
                    g._duoBB[i] = LerpI(aHiB[i], bHiB[i], t);
                }
                g.RebuildDuoDelta();
                // HasDuo is a plain field that Compile() sets, and the clone inherited
                // false from a ramp grade, so SampleCore would have taken the identity
                // path and returned the input untouched.
                g.HasDuo = true;
                g._rampR = null; g._rampG = null; g._rampB = null;
                g._luma256 = (int)Math.Round(a._luma256 + (b._luma256 - a._luma256) * t);
                return g;
            }

            g._luma256 = (int)Math.Round(a._luma256 + (b._luma256 - a._luma256) * t);
            return g;
        }

        /// <summary>True when the grade maps luminance (and at most a selector) to colour,
        /// i.e. it is a ramp or a duo - the two forms that can be crossfaded exactly.</summary>
        internal bool IsRampOrDuo { get { return _rampR != null || _duoAR != null; } }

        private static int LerpI(int x, int y, float t)
        {
            return (int)Math.Round(x + (y - x) * t);
        }

        private static byte LerpB(byte x, byte y, float t)
        {
            int v = (int)Math.Round(x + (y - x) * t);
            return (byte)(v < 0 ? 0 : (v > 255 ? 255 : v));
        }
    }

    // ---------------------------------------------------------------- settings

    internal sealed class Options
    {
        public string Palette = "native";
        public string GradeSpec = null;
        public float Speed = 1.0f;
        public int SecondsPerLoop = 0;       // 0 = whole clip
        public string Render = "1920x1080";
        public bool Hud = false;
        public bool Loop = true;
        public bool NoShift = false;
        public int ShiftAmplitude = 2;
        public float Zoom = 1.0f;
        public bool Mirror = false;
        public bool Kaleido = false;
        public float Pulse = 0f;
        public double Minutes = 0;
        public int IdleSeconds = 0;
        public bool Fill = true;             // cover (crop) vs letterbox
        public string Source = null;
        public bool Verbose = false;

        // colour dynamics
        public float Luma = 0f;              // dose target, 0..1 mean luminance
        public string Duo = null;            // "#a,#b" two-ink duotone
        public string Progress = null;       // palette to ramp toward over the session
        public double ProgressMinutes = 0;


        // pattern / motion
        public bool TriadShift = true;       // --shift counts RGB triads, not raw pixels
        public bool Orbit = false;           // step the crop centre 90 deg each loop
        public bool Dwell = false;           // bias the orbit toward least-exercised regions
        public int RotateQuadrant = -1;      // force a starting crop quadrant
        public float Ripple = 0f;            // px of animated wave displacement
        public float Scan = 0f;              // 0..1 scanline darkening
        public float Bloom = 0f;             // 0..1 glow add-back
        public float Grain = 0f;             // 0..1 film grain
        public float Gamma = 1f;             // extra gamma on top of the palette
        public float Heal = 0f;              // 0..1 dissolve across the source's black gaps
        public float BlendPeriod = 60f;      // seconds for a "a+b" palette sweep

        // output
        public string Export = null;         // write a video instead of playing
        public string ExportSize = "1920x1080";
        public double ExportSeconds = 60;
        public string Ffmpeg = null;
        public string ExportAll = null;      // batch: one clip per palette into this dir
        public string Palettes = null;       // batch: restrict to these palette names

        // shell integration
        public bool InstallScr = false;
        public bool UninstallScr = false;
        public int ScrTimeout = 0;

        public static Options Parse(string[] args)
        {
            Options o = new Options();
            for (int i = 0; i < args.Length; i++)
            {
                string a = args[i];
                string next = (i + 1 < args.Length) ? args[i + 1] : null;
                switch (a)
                {
                    case "--palette": if (next != null) { o.Palette = next; i++; } break;
                    case "--grade": if (next != null) { o.GradeSpec = next; i++; } break;
                    case "--speed": if (next != null) { o.Speed = ParseF(next, 1.0f); i++; } break;
                    case "--seconds": if (next != null) { o.SecondsPerLoop = (int)ParseF(next, 0); i++; } break;
                    case "--render": if (next != null) { o.Render = next; i++; } break;
                    case "--zoom": if (next != null) { o.Zoom = ParseF(next, 1.0f); i++; } break;
                    case "--pulse": if (next != null) { o.Pulse = ParseF(next, 0f); i++; } break;
                    case "--shift": if (next != null) { o.ShiftAmplitude = (int)ParseF(next, 2); i++; } break;
                    case "--minutes": if (next != null) { o.Minutes = ParseF(next, 0); i++; } break;
                    case "--idle": if (next != null) { o.IdleSeconds = (int)ParseF(next, 0); i++; } break;
                    case "--source": if (next != null) { o.Source = next; i++; } break;
                    case "--hud": o.Hud = true; break;
                    case "--mirror": o.Mirror = true; break;
                    case "--kaleido": o.Kaleido = true; break;
                    case "--no-shift": o.NoShift = true; break;
                    case "--no-loop": o.Loop = false; break;
                    case "--letterbox": o.Fill = false; break;
                    case "--verbose": o.Verbose = true; break;
                    case "--luma": if (next != null) { o.Luma = ParseF(next, 0f); i++; } break;
                    case "--duo": if (next != null) { o.Duo = next; i++; } break;
                    case "--progress": if (next != null) { o.Progress = next; i++; } break;
                    case "--progress-minutes": if (next != null) { o.ProgressMinutes = ParseF(next, 0); i++; } break;
                    case "--shift-px": o.TriadShift = false; break;
                    case "--orbit": o.Orbit = true; break;
                    case "--dwell": o.Dwell = true; break;
                    case "--quadrant": if (next != null) { o.RotateQuadrant = (int)ParseF(next, 0); i++; } break;
                    case "--ripple": if (next != null) { o.Ripple = ParseF(next, 0f); i++; } break;
                    case "--scan": if (next != null) { o.Scan = ParseF(next, 0f); i++; } break;
                    case "--bloom": if (next != null) { o.Bloom = ParseF(next, 0f); i++; } break;
                    case "--grain": if (next != null) { o.Grain = ParseF(next, 0f); i++; } break;
                    case "--gamma": if (next != null) { o.Gamma = ParseF(next, 1f); i++; } break;
                    case "--heal": if (next != null) { o.Heal = ParseF(next, 0f); i++; } break;
                    case "--blend-period": if (next != null) { o.BlendPeriod = ParseF(next, 60f); i++; } break;
                    case "--export": if (next != null) { o.Export = next; i++; } break;
                    case "--export-size": if (next != null) { o.ExportSize = next; i++; } break;
                    case "--export-seconds": if (next != null) { o.ExportSeconds = ParseF(next, 60f); i++; } break;
                    case "--export-all": if (next != null) { o.ExportAll = next; i++; } break;
                    case "--palettes": if (next != null) { o.Palettes = next; i++; } break;
                    case "--ffmpeg": if (next != null) { o.Ffmpeg = next; i++; } break;
                    case "--install-scr": o.InstallScr = true; break;
                    case "--uninstall-scr": o.UninstallScr = true; break;
                    case "--scr-timeout": if (next != null) { o.ScrTimeout = (int)ParseF(next, 0); i++; } break;
                }
            }
            return o;
        }

        private static float ParseF(string s, float dflt)
        {
            float r;
            if (float.TryParse(s, NumberStyles.Float, CultureInfo.InvariantCulture, out r)) return r;
            return dflt;
        }
    }

    /// <summary>
    /// Keeps the four orbit positions evenly exercised. Each position accumulates the
    /// mean luminance it showed while it was on screen, and the next loop is given to
    /// whichever position has the lowest luminance-seconds so far - so the bright
    /// passages of the clip spread across the panel instead of always landing on the
    /// same columns. First visit always goes to a position that has not been used.
    /// </summary>
    internal sealed class Dwell
    {
        private readonly double[] _dose = new double[4];
        private readonly int[] _visits = new int[4];

        public void Add(int q, double meanLuma)
        {
            int i = ((q % 4) + 4) % 4;
            _dose[i] += meanLuma;
            _visits[i]++;
        }

        public int Next(int fallback)
        {
            int best = -1;
            double bestV = 0;
            for (int i = 0; i < 4; i++)
            {
                // unvisited wins outright; a plain 0 would tie with a genuinely dark slot
                double v = _visits[i] == 0 ? -1.0 : _dose[i] / _visits[i];
                if (best < 0 || v < bestV) { best = i; bestV = v; }
            }
            return best < 0 ? fallback : best;
        }

        public void Report()
        {
            for (int i = 0; i < 4; i++)
            {
                Console.Error.WriteLine(string.Format(CultureInfo.InvariantCulture,
                    "dwell {0}: {1} loops, mean luma {2:F3}",
                    i, _visits[i], _visits[i] == 0 ? 0.0 : _dose[i] / _visits[i]));
            }
        }
    }

    // ---------------------------------------------------------------- decoder

    /// <summary>
    /// The vendor footage dips to black at every 15 s junction - that is its own
    /// crossfade, not a decode failure. --heal dissolves across those dips: it holds the
    /// last fully-lit frame and hands it back in proportion to how dark the incoming one
    /// is, so the gap reads as a slow push through the smoke instead of a cut to black.
    /// The hold is only refreshed on well-lit frames: holding at the gap threshold itself
    /// would freeze the frame that is already halfway to black, and the healed stretch
    /// would come out dim.
    /// </summary>
    internal sealed class Healer
    {
        private readonly int _w, _h, _bytes;
        private readonly float _strength;
        private readonly byte[] _hold, _emit;
        private bool _haveHold;
        private const float DarkY = 0.055f;     // mean luminance below this is a gap
        private const float LitY = 0.20f;       // ...and above this a frame is worth holding

        public Healer(int w, int h, float strength)
        {
            _w = w; _h = h; _bytes = w * h * 4;
            _strength = strength > 1f ? 1f : (strength < 0f ? 0f : strength);
            _hold = new byte[_bytes];
            _emit = new byte[_bytes];
        }

        public bool HaveHold { get { return _haveHold; } }

        /// <summary>Seeds the hold from a known-lit frame, so the leading dip at t=0 is
        /// covered too. Without this the first quarter-second stays black.</summary>
        public void Seed(byte[] src)
        {
            if (src.Length < _bytes) return;
            Buffer.BlockCopy(src, 0, _hold, 0, _bytes);
            _haveHold = true;
        }

        /// <summary>Returns the buffer to grade: the frame itself, or the healed stand-in.</summary>
        public byte[] Feed(byte[] src)
        {
            if (src.Length < _bytes) return src;
            double lum = Luma(src);
            if (lum >= LitY)
            {
                Buffer.BlockCopy(src, 0, _hold, 0, _bytes);
                _haveHold = true;
            }

            // k runs 1..0 across the fade rather than switching at the gap threshold, so
            // there is no pop the moment a frame is declared dark.
            float k = (float)((lum - DarkY) / (LitY - DarkY));
            if (k > 1f) k = 1f;
            if (k < 0f) k = 0f;
            if (k >= 0.999f) return src;
            if (!_haveHold) return src;

            // strength 1 holds fully; 0 leaves the dip exactly as the vendor cut it
            float t = k + (1f - k) * (1f - _strength);
            if (t >= 0.999f) return src;
            Blend(_hold, src, _emit, t);
            return _emit;
        }

        private static void Blend(byte[] a, byte[] b, byte[] dst, float t)
        {
            int ti = (int)(t * 256f);
            int ai = 256 - ti;
            for (int i = 0; i < dst.Length; i++)
                dst[i] = (byte)((b[i] * ti + a[i] * ai) >> 8);
        }

        /// <summary>Sparse mean luminance: an eighth of the rows and columns is plenty to
        /// tell a dip from a lit frame, and a full pass would cost as much as the blit.</summary>
        private double Luma(byte[] f)
        {
            long sum = 0;
            int n = 0;
            for (int y = 0; y < _h; y += 8)
            {
                int row = y * _w * 4;
                for (int x = 0; x < _w; x += 8)
                {
                    int i = row + x * 4;
                    sum += (f[i] * 29 + f[i + 1] * 150 + f[i + 2] * 77) >> 8;
                    n++;
                }
            }
            return n == 0 ? 0.0 : (double)sum / (n * 255.0);
        }
    }

    internal sealed class SmokeSource : IDisposable
    {
        private IMFSourceReader _reader;
        private int _w, _h;
        private bool _bottomUp;

        public int Width { get { return _w; } }
        public int Height { get { return _h; } }
        public bool BottomUp { get { return _bottomUp; } }

        public static SmokeSource Open(string path, int targetW, int targetH)
        {
            int hr = MF.MFStartup(MF.MF_VERSION, MF.MFSTARTUP_FULL);
            if (hr < 0) throw new InvalidOperationException("MFStartup failed 0x" + hr.ToString("X8"));

            IMFAttributes attrs;
            hr = MF.MFCreateAttributes(out attrs, 4);
            if (hr < 0) throw new InvalidOperationException("MFCreateAttributes failed");
            Guid key = MF.MF_SOURCE_READER_ENABLE_VIDEO_PROCESSING;
            attrs.SetUINT32(ref key, 1);

            IMFSourceReader reader;
            hr = MF.MFCreateSourceReaderFromURL(path, attrs, out reader);
            if (hr < 0) throw new InvalidOperationException("MFCreateSourceReaderFromURL failed 0x" + hr.ToString("X8"));

            SmokeSource s = new SmokeSource();
            s._reader = reader;

            // let the video processor convert + scale to RGB32
            IMFMediaType mt;
            hr = MF.MFCreateMediaType(out mt);
            if (hr < 0) throw new InvalidOperationException("MFCreateMediaType failed");
            Guid kMajor = MF.MF_MT_MAJOR_TYPE, kSub = MF.MF_MT_SUBTYPE, kSize = MF.MF_MT_FRAME_SIZE;
            Guid vids = MF.MFMediaType_Video, rgb = MF.MFVideoFormat_RGB32;
            mt.SetGUID(ref kMajor, ref vids);
            mt.SetGUID(ref kSub, ref rgb);
            ulong packed = ((ulong)(uint)targetW << 32) | (uint)targetH;
            mt.SetUINT64(ref kSize, packed);

            hr = reader.SetCurrentMediaType(MF.MF_SOURCE_READER_FIRST_VIDEO_STREAM, IntPtr.Zero, mt);
            if (hr < 0)
            {
                // retry with only the subtype pinned, so the decoder keeps its native size
                hr = MF.MFCreateMediaType(out mt);
                mt.SetGUID(ref kMajor, ref vids);
                mt.SetGUID(ref kSub, ref rgb);
                hr = reader.SetCurrentMediaType(MF.MF_SOURCE_READER_FIRST_VIDEO_STREAM, IntPtr.Zero, mt);
                if (hr < 0) throw new InvalidOperationException("SetCurrentMediaType(RGB32) failed 0x" + hr.ToString("X8"));
            }

            IMFMediaType cur;
            hr = reader.GetCurrentMediaType(MF.MF_SOURCE_READER_FIRST_VIDEO_STREAM, out cur);
            if (hr >= 0 && cur != null)
            {
                ulong fs;
                Guid kFs = MF.MF_MT_FRAME_SIZE;
                if (cur.GetUINT64(ref kFs, out fs) >= 0)
                {
                    s._w = (int)(fs >> 32);
                    s._h = (int)(fs & 0xFFFFFFFF);
                }
                uint stride;
                Guid kStride = MF.MF_MT_DEFAULT_STRIDE;
                if (cur.GetUINT32(ref kStride, out stride) >= 0)
                    s._bottomUp = unchecked((int)stride) < 0;
            }
            if (s._w <= 0 || s._h <= 0) { s._w = targetW; s._h = targetH; }
            return s;
        }

        /// <summary>Why the last Next() returned null, when it was not simply end of stream.</summary>
        public string LastError = "";
        public long LastTimestamp = -1;
        public int LastFlags = -1;

        /// <summary>Empty samples the reader delivered before the last good frame.</summary>
        public int LastEmptySamples;

        /// <summary>
        /// Reads the next frame. Returns null at end of stream. The source reader occasionally
        /// hands back a sample with no buffers (a gap/discontinuity marker); those are skipped.
        /// </summary>
        public byte[] Next()
        {
            LastEmptySamples = 0;
            for (int attempt = 0; attempt < 64; attempt++)
            {
                int actual, flags;
                long ts;
                IntPtr pSample;
                int hr = _reader.ReadSample(MF.MF_SOURCE_READER_FIRST_VIDEO_STREAM, 0, out actual, out flags,
                                            out ts, out pSample);
                LastTimestamp = ts; LastFlags = flags;
                if (hr < 0) { LastError = "ReadSample hr=0x" + hr.ToString("X8"); return null; }
                if ((flags & MF.MF_SOURCE_READERF_ENDOFSTREAM) != 0) return null;
                if (pSample == IntPtr.Zero)
                {
                    LastEmptySamples++;
                    continue;
                }

                IMFSample sample;
                try { sample = (IMFSample)Marshal.GetObjectForIUnknown(pSample); }
                catch (Exception ex)
                {
                    LastError = "sample cast failed: " + ex.Message;
                    Marshal.Release(pSample);
                    return null;
                }
                Marshal.Release(pSample);

                IMFMediaBuffer buf = null;
                int bufferCount;
                hr = sample.GetBufferCount(out bufferCount);
                if (hr < 0)
                {
                    LastError = "GetBufferCount hr=0x" + hr.ToString("X8");
                    return null;
                }
                if (bufferCount == 0)
                {
                    LastEmptySamples++;
                    Marshal.ReleaseComObject(sample);
                    continue;
                }
                if (hr >= 0 && bufferCount == 1)
                    hr = sample.GetBufferByIndex(0, out buf);
                else
                    hr = sample.ConvertToContiguousBuffer(out buf);
                Marshal.ReleaseComObject(sample);
                if (hr < 0 || buf == null)
                {
                    LastError = "buffer fetch hr=0x" + hr.ToString("X8") + " count=" + bufferCount;
                    return null;
                }

                IntPtr p;
                int max, len;
                hr = buf.Lock(out p, out max, out len);
                if (hr < 0) { LastError = "Lock hr=0x" + hr.ToString("X8"); return null; }
                try
                {
                    byte[] data = new byte[len];
                    Marshal.Copy(p, data, 0, len);
                    return data;
                }
                finally
                {
                    buf.Unlock();
                    Marshal.ReleaseComObject(buf);
                }
            }
            LastError = "64 samples in a row had no buffer";
            return null;
        }

        public void Rewind()
        {
            Guid tf = Guid.Empty;
            PropVariant pv = new PropVariant();
            pv.vt = 20;      // VT_I8
            pv.hVal = 0;
            _reader.SetCurrentPosition(ref tf, ref pv);
            _reader.Flush(MF.MF_SOURCE_READER_FIRST_VIDEO_STREAM);
        }

        public void Dispose()
        {
            if (_reader != null)
            {
                Marshal.ReleaseComObject(_reader);
                _reader = null;
            }
            MF.MFShutdown();
        }
    }

    // ---------------------------------------------------------------- renderer

    internal sealed class Renderer
    {
        private Grade _grade;
        private readonly Options _opt;
        private readonly int _w, _h;

        public Renderer(Grade grade, Options opt, int w, int h)
        {
            _grade = grade;
            _opt = opt;
            _w = w;
            _h = h;
        }

        /// <summary>Swap the grade between frames (progress ramp). Only call from the
        /// thread that owns the render loop.</summary>
        public void SetGrade(Grade g) { _grade = g; }

        /// <summary>Crossfades the grade toward <paramref name="b"/> and back over one
        /// loop. The sweep is a raised cosine, so t=0 at the seam and at the wrap - a
        /// linear ramp would jump from b straight back to a every time the clip loops.
        /// The blend happens in the baked tables, so the pixel cost stays a single grade.</summary>
        public void SetBlendPair(Grade b)
        {
            _blendA = _grade;
            _blendB = b;
            _blendPeriod = _opt.BlendPeriod > 1f ? _opt.BlendPeriod : 60f;
            _blendStep = -1;
            // A hue/sat/gain palette is not a function of luminance, so it cannot be
            // crossfaded with a ramp or duo one (two of those mix fine, and so do two
            // hue/sat/gain ones). Say so rather than rendering a frame that quietly
            // belongs to the first palette.
            if (_grade.IsRampOrDuo != b.IsRampOrDuo)
            {
                _blendB = null;
                try
                {
                    Console.Error.WriteLine("note: --palette \"a+b\" needs both sides to be ramp or " +
                                            "duo palettes (e.g. neon-cyan+yt-deep, duo-cyan+duo-sun); " +
                                            _grade.Name + " + " + b.Name + " cannot crossfade, using " +
                                            _grade.Name);
                }
                catch (Exception) { }
            }
        }

        /// <summary>Source-space offset of the sampling centre, used by --orbit to move
        /// the crop window without stretching anything. Clamped per frame so the window
        /// never leaves the decoded frame (a clamp in the sampler would smear the edge).</summary>
        public float OrbitX, OrbitY;

        /// <summary>Seconds into the clip. The animated effects read only this, so the
        /// export and the live player agree frame for frame.</summary>
        public float Time;

        // effect scratch. Reused across frames: at 1080p the ripple tables are two
        // ~2k-entry arrays and the bloom buffer is 240x135, so per-frame allocation
        // would be pure garbage.
        private float[] _ripX, _ripY;
        private int[] _scanMul;
        private int _scanH;
        private float _scanS = -1f;
        // Bloom is built from the frame being written and added back on the NEXT one.
        // One frame of lag at 24 fps is invisible behind an 8x8 blur, and it removes a
        // whole full-resolution pass: the candle is cheaper than the read-back.
        private float[] _accR = new float[1], _accG = new float[1], _accB = new float[1], _accW = new float[1], _blurTmp;
        // The glow plane is a power-of-two block, so mapping a pixel to its cell is a
        // shift instead of a table lookup. At 1/8 the three byte planes were 243 KB at
        // panel size - outside L2 - and the per-pixel bilinear tap cost six reads into
        // them. Packing the three channels into one uint and dropping the tap (the plane
        // is already blurred, so nearest cannot show) took bloom from 107 ms to ~20 ms.
        private const int BloomShift = 4;
        private const int BloomBlock = 1 << BloomShift;
        private uint[] _glow = new uint[1];   // packed 0xRRGGBB, pre-scaled by the add amount
        private int _bmW, _bmH;
        private bool _glowReady;
        private int _bloomFrame;
        private int _glowAdd = 256;
        // grain: a 128x128 signed-noise tile, so the per-pixel cost is one load
        private sbyte[] _grainTab = new sbyte[1];
        private float _grainS = -1f;
        // palette blend: --palette "a+b" sweeps a to b and back over the loop
        private Grade _blendA, _blendB;
        private float _blendPeriod = 60f;
        private int _blendStep = -1;

        /// <summary>Moves the crop window to one of four positions around centre. The
        /// window only has room on the axis the cover-crop trimmed, so a position with no
        /// room degrades to centre rather than to a smeared edge.</summary>
        public void SetOrbitQuadrant(Size dst, int quadrant)
        {
            int q = ((quadrant % 4) + 4) % 4;
            float zoom = _opt.Zoom <= 0.01f ? 1f : _opt.Zoom;
            float coverX = (float)dst.Width / _w, coverY = (float)dst.Height / _h;
            zoom *= coverX > coverY ? coverX : coverY;
            float roomX = (_w - dst.Width / zoom) * 0.5f;
            float roomY = (_h - dst.Height / zoom) * 0.5f;
            if (roomX < 0) roomX = 0;
            if (roomY < 0) roomY = 0;
            switch (q)
            {
                case 1: OrbitX = roomX; OrbitY = 0; break;
                case 2: OrbitX = 0; OrbitY = -roomY; break;
                case 3: OrbitX = -roomX; OrbitY = 0; break;
                default: OrbitX = 0; OrbitY = 0; break;
            }
        }

        /// <summary>Grades one decoded RGB32 frame into a 32bpp bitmap.</summary>
        public unsafe void Blit(byte[] src, bool bottomUp, Bitmap dst, float pulse, int shiftX, int shiftY, int loopParity)
        {
            // Palette sweep. Rebuilding the baked tables 128 times per loop is ~40 us a
            // rebuild, i.e. nothing, and quantising to 128 steps keeps it near 128/s once
            // the drift is that slow.
            if (_blendB != null)
            {
                double ph = (Time / _blendPeriod) * Math.PI * 2.0;
                float bt = (float)(0.5 - 0.5 * Math.Cos(ph));
                int step = (int)(bt * 128f);
                if (step != _blendStep)
                {
                    _blendStep = step;
                    _grade = Grade.Blend(_blendA, _blendB, step / 128f);
                }
            }

            BitmapData bd = dst.LockBits(new Rectangle(0, 0, dst.Width, dst.Height),
                                         ImageLockMode.WriteOnly, PixelFormat.Format32bppRgb);
            try
            {
                int[] m = _grade._m;
                byte[] lr = _grade._lutR, lg = _grade._lutG, lb = _grade._lutB;
                int[] rr = _grade._rampR, rg = _grade._rampG, rb = _grade._rampB;
                int mix = _grade._mix256;
                int[] dAR = _grade._duoAR, dAG = _grade._duoAG, dAB = _grade._duoAB;
                int[] dDR = _grade._duoDR, dDG = _grade._duoDG, dDB = _grade._duoDB;
                bool duo = dAR != null && dDR != null;
                int luma = _grade._luma256;

                int m0 = m[0], m1 = m[1], m2 = m[2], m3 = m[3], m4 = m[4], m5 = m[5], m6 = m[6], m7 = m[7], m8 = m[8];
                int pr = (int)(pulse * 256), pg = pr, pb = pr;

                int dw = dst.Width, dh = dst.Height;
                float zoom = _opt.Zoom <= 0.01f ? 1f : _opt.Zoom;
                // Cover-crop in the sampler. Without this, rendering into a larger
                // bitmap pushed the sample point past the source edge and smeared the
                // outer border pixels instead of cropping. max() also gives a true
                // downscale when the target is smaller (min() would crop).
                float coverX = (float)dw / _w, coverY = (float)dh / _h;
                zoom *= coverX > coverY ? coverX : coverY;

                // Orbit: slide the whole crop window, clamped to the room it actually
                // has. Without the clamp the sampler's own edge clamp would smear the
                // outermost columns, which is exactly the artefact this avoids.
                float roomX = (_w - dw / zoom) * 0.5f;
                float roomY = (_h - dh / zoom) * 0.5f;
                if (roomX < 0) roomX = 0;
                if (roomY < 0) roomY = 0;
                float ox = OrbitX < -roomX ? -roomX : (OrbitX > roomX ? roomX : OrbitX);
                float oy = OrbitY < -roomY ? -roomY : (OrbitY > roomY ? roomY : OrbitY);
                float cx = _w * 0.5f + ox, cy = _h * 0.5f + oy;

                byte* db = (byte*)bd.Scan0;
                int dstride = bd.Stride;

                // Effect tables are rebuilt once per frame, never per pixel: a sin() in
                // the inner loop would cost more than the whole grade does.
                float[] ripX = _opt.Ripple > 0.01f ? BuildRippleX(dw) : null;
                float[] ripY = _opt.Ripple > 0.01f ? BuildRippleY(dh) : null;
                int[] scanMul = _opt.Scan > 0.001f ? BuildScan(dh) : null;

                // The glow field is rebuilt on every other frame. It lives behind an
                // 8x blur and is added back for 2-3 frames anyway, so at 24 fps the
                // difference is invisible - and it halves the one cost that scales with
                // pixel count on a 2880x1800 panel.
                bool bloom = _opt.Bloom > 0.001f;
                int bw = 0;
                bool accumulating = false, useGlow = false;
                if (bloom)
                {
                    bw = (dw + BloomBlock - 1) >> BloomShift;
                    int bh = (dh + BloomBlock - 1) >> BloomShift;
                    accumulating = (_bloomFrame++ & 1) == 0;
                    _glowAdd = (int)((_opt.Bloom > 1f ? 1f : _opt.Bloom) * 256f);
                    BeginBloom(bw, bh, accumulating);
                    useGlow = _glowReady;
                }

                // Grain is a monochrome delta from a tiled table - a per-pixel hash would
                // cost a multiply and a store the inner loop cannot spare.
                sbyte[] grainTab = _grainTab;
                float grainAmt = _opt.Grain > 1f ? 1f : _opt.Grain;
                bool grainOn = grainAmt > 0.001f;
                if (grainOn) grainTab = BuildGrain(grainAmt);
                int gShiftX = 0, gShiftY = 0;
                if (grainOn)
                {
                    int gs = (int)(Time * 61f);       // 61 steps/s: the tile never marches
                    gShiftX = (gs * 37) & 127;
                    gShiftY = (gs * 11) & 127;
                }

                // Raw pointers for the effect buffers too: these are read once per
                // pixel, and the bounds check on a managed array read cost more than
                // the arithmetic it guarded (~30 ms/frame at 1080p).
                fixed (byte* sb = src)
                fixed (uint* glowp = _glow)
                fixed (float* acR = _accR)
                fixed (float* acG = _accG)
                fixed (float* acB = _accB)
                fixed (float* acW = _accW)
                fixed (sbyte* grainp = grainTab)
                {
                    for (int y = 0; y < dh; y++)
                    {
                        // vertically nearest: the plane is already blurred at 8x, so a
                        // second vertical lerp costs as much as it buys (nothing).
                        int glowRow = (y >> BloomShift) * bw;
                        int accRow = (y >> BloomShift) * bw;
                        // The bright pass runs on every other row and column: a 1/16 cell
                        // still gets 64 samples, and the plane is blurred before it is used.
                        bool accHere = accumulating && ((y & 1) == 0);
                        sbyte* grow = grainOn ? grainp + (((y + gShiftY) & 127) << 7) : grainp;
                        byte* row = db + y * dstride;
                        // source row through zoom + shift + mirror/kaleido
                        float sy = cy + (y - dh * 0.5f) / zoom + shiftY + (ripY != null ? ripY[y] : 0f);
                        int y0 = (int)sy;
                        if (_opt.Mirror && (loopParity & 1) == 1) y0 = _h - 1 - y0;
                        if (_opt.Kaleido) y0 = Fold(y0, _h);
                        if (y0 < 0) y0 = 0; if (y0 >= _h) y0 = _h - 1;
                        int srcRow = bottomUp ? (_h - 1 - y0) : y0;
                        byte* srow = sb + srcRow * _w * 4;

                        for (int x = 0; x < dw; x++)
                        {
                            float sx = cx + (x - dw * 0.5f) / zoom + shiftX + (ripX != null ? ripX[x] : 0f);
                            int x0 = (int)sx;
                            if (_opt.Mirror && (loopParity & 1) == 1) x0 = _w - 1 - x0;
                            if (_opt.Kaleido) x0 = Fold(x0, _w);
                            if (x0 < 0) x0 = 0; if (x0 >= _w) x0 = _w - 1;

                            byte* sp = srow + x0 * 4;
                            int b = sp[0], g = sp[1], r = sp[2];

                            int nr = (m0 * r + m1 * g + m2 * b) >> 8;
                            int ng = (m3 * r + m4 * g + m5 * b) >> 8;
                            int nb = (m6 * r + m7 * g + m8 * b) >> 8;
                            // Branchless clamp. Saturation above 1 pushes roughly half the
                            // pixels out of range, so the branchy version mispredicted on
                            // the bench's noise and cost ~3x. These four lines are
                            // arithmetic only and cannot mispredict.
                            nr &= ~(nr >> 31); ng &= ~(ng >> 31); nb &= ~(nb >> 31);
                            int dc;
                            dc = nr - 255; nr -= dc & ~(dc >> 31);
                            dc = ng - 255; ng -= dc & ~(dc >> 31);
                            dc = nb - 255; nb -= dc & ~(dc >> 31);
                            nr = lr[nr]; ng = lg[ng]; nb = lb[nb];

                            int orr, og, ob;
                            if (duo)
                            {
                                int yy = (nr * 77 + ng * 150 + nb * 29) >> 8;
                                // The two dyes sit on opposite sides of blue-minus-green.
                                // 128/160 is 0.8, and (x*410)>>9 is 0.8008 - close enough to
                                // pick a dye, and it keeps a division out of the pixel loop.
                                int sel = 128 + (((b - g) * 410) >> 9);
                                sel &= ~(sel >> 31);
                                int ds = sel - 255; sel -= ds & ~(ds >> 31);
                                // The blend is a straight line in the selector, so one
                                // table plus a multiply replaces two tables and a divide.
                                orr = dAR[yy] + ((dDR[yy] * sel) >> 8);
                                og = dAG[yy] + ((dDG[yy] * sel) >> 8);
                                ob = dAB[yy] + ((dDB[yy] * sel) >> 8);
                            }
                            else if (rr != null)
                            {
                                int yy = (nr * 77 + ng * 150 + nb * 29) >> 8;
                                orr = rr[yy]; og = rg[yy]; ob = rb[yy];
                            }
                            else { orr = nr; og = ng; ob = nb; }

                            if (luma != 256)
                            {
                                orr = (orr * luma) >> 8; og = (og * luma) >> 8; ob = (ob * luma) >> 8;
                                if (orr > 255) orr = 255; if (og > 255) og = 255; if (ob > 255) ob = 255;
                            }

                            if (pulse != 1f)
                            {
                                orr = (orr * pr) >> 8; og = (og * pg) >> 8; ob = (ob * pb) >> 8;
                                if (orr > 255) orr = 255; if (og > 255) og = 255; if (ob > 255) ob = 255;
                            }
                            if (mix != 256)
                            {
                                orr = (orr * mix + r * (256 - mix)) >> 8;
                                og = (og * mix + g * (256 - mix)) >> 8;
                                ob = (ob * mix + b * (256 - mix)) >> 8;
                            }

                            if (scanMul != null)
                            {
                                int sm = scanMul[y];
                                orr = (orr * sm) >> 8; og = (og * sm) >> 8; ob = (ob * sm) >> 8;
                            }                            // glow from the previous frame's blurred bright pass. One packed
                            // load replaces the six across three byte planes, and the scale
                            // was folded in when the plane was packed.
                            if (useGlow)
                            {
                                uint gp = glowp[glowRow + (x >> BloomShift)];
                                int v, d2;
                                v = orr + (int)((gp >> 16) & 0xFF);
                                d2 = v - 255; orr = v - (d2 & ~(d2 >> 31));
                                v = og + (int)((gp >> 8) & 0xFF);
                                d2 = v - 255; og = v - (d2 & ~(d2 >> 31));
                                v = ob + (int)(gp & 0xFF);
                                d2 = v - 255; ob = v - (d2 & ~(d2 >> 31));
                            }

                            // grain is signed, so it needs both ends clamped
                            if (grainOn)
                            {
                                int gv = grow[(x + gShiftX) & 127];
                                int v, lo, d2;
                                v = orr + gv; lo = v >> 31; v &= ~lo; d2 = v - 255; orr = v - (d2 & ~(d2 >> 31));
                                v = og + gv; lo = v >> 31; v &= ~lo; d2 = v - 255; og = v - (d2 & ~(d2 >> 31));
                                v = ob + gv; lo = v >> 31; v &= ~lo; d2 = v - 255; ob = v - (d2 & ~(d2 >> 31));
                            }

                            if (accHere && (x & 1) == 0)
                            {
                                int lum2 = (orr * 77 + og * 150 + ob * 29) >> 8;
                                int tt = lum2 - 120;
                                if (tt > 0)
                                {
                                    if (tt > 135) tt = 135;
                                    float w2 = tt * 0.0074074f;              // 1/135
                                    int bi = accRow + (x >> BloomShift);
                                    acR[bi] += orr * w2; acG[bi] += og * w2;
                                    acB[bi] += ob * w2;  acW[bi] += w2;
                                }
                            }

                            byte* dp = row + x * 4;
                            dp[0] = (byte)ob;
                            dp[1] = (byte)og;
                            dp[2] = (byte)orr;
                            dp[3] = 255;
                        }
                    }
                }

                if (accumulating) EndBloom();
            }
            finally
            {
                dst.UnlockBits(bd);
            }
        }

        private static int Fold(int v, int n)
        {
            int period = n * 2;
            int t = ((v % period) + period) % period;
            return t < n ? t : period - 1 - t;
        }

        // ---- --ripple: a slow travelling wave through the sample coordinates.
        // Two long wavelengths crossed at different speeds, so the plumes shear
        // against each other instead of sliding as one sheet.

        private float[] BuildRippleX(int dw)
        {
            if (_ripX == null || _ripX.Length < dw) _ripX = new float[dw];
            float amp = _opt.Ripple;
            float k = 6.2831853f / 320f;
            float ph = Time * 0.85f;
            for (int x = 0; x < dw; x++) _ripX[x] = amp * (float)Math.Sin(x * k + ph);
            return _ripX;
        }

        private float[] BuildRippleY(int dh)
        {
            if (_ripY == null || _ripY.Length < dh) _ripY = new float[dh];
            float amp = _opt.Ripple * 0.45f;
            float k = 6.2831853f / 230f;
            float ph = Time * 0.62f + 1.7f;
            for (int y = 0; y < dh; y++) _ripY[y] = amp * (float)Math.Sin(y * k - ph);
            return _ripY;
        }

        // ---- --scan: per-row multiplier, 4-row period, cached on (height, strength).

        private int[] BuildScan(int dh)
        {
            float s = _opt.Scan;
            if (s > 1f) s = 1f;
            if (_scanMul == null || _scanH != dh || _scanS != s)
            {
                _scanMul = new int[dh];
                _scanH = dh;
                _scanS = s;
                for (int y = 0; y < dh; y++)
                {
                    float t = 0.5f + 0.5f * (float)Math.Cos(y * 1.5707963);  // 0..1, period 4
                    _scanMul[y] = 256 - (int)(s * 118f * t);
                }
            }
            return _scanMul;
        }

        // ---- --bloom: bright-pass into a 1/16 plane, box-blur it, nearest add-back.
        // The plane is 180x113 at panel size (81 KB packed), so it stays resident instead
        // of being re-fetched from L3 on every pixel.

        private void BeginBloom(int bw, int bh, bool clear)
        {
            if (_bmW != bw || _bmH != bh)
            {
                _bmW = bw; _bmH = bh;
                _accR = new float[bw * bh]; _accG = new float[bw * bh];
                _accB = new float[bw * bh]; _accW = new float[bw * bh];
                _glow = new uint[bw * bh];
                _glowReady = false;
            }
            if (clear)
            {
                Array.Clear(_accR, 0, _accR.Length);
                Array.Clear(_accG, 0, _accG.Length);
                Array.Clear(_accB, 0, _accB.Length);
                Array.Clear(_accW, 0, _accW.Length);
            }
        }

        /// <summary>Normalises what the sampling loop accumulated, blurs it, and parks it
        /// for the next frame to add back. The add amount is folded in here because it is
        /// constant for a run - so the inner loop only has to add bytes.</summary>
        private void EndBloom()
        {
            int n = _bmW * _bmH;
            for (int i = 0; i < n; i++)
            {
                float w = _accW[i];
                if (w > 0.001f)
                {
                    _accR[i] /= w; _accG[i] /= w; _accB[i] /= w;
                }
                else { _accR[i] = 0f; _accG[i] = 0f; _accB[i] = 0f; }
            }
            Blur(_accR, _bmW, _bmH);
            Blur(_accG, _bmW, _bmH);
            Blur(_accB, _bmW, _bmH);
            float a = _glowAdd * 0.00390625f;
            for (int i = 0; i < n; i++)
            {
                int r = (int)(_accR[i] * a);
                int g = (int)(_accG[i] * a);
                int b = (int)(_accB[i] * a);
                if (r > 255) r = 255; else if (r < 0) r = 0;
                if (g > 255) g = 255; else if (g < 0) g = 0;
                if (b > 255) b = 255; else if (b < 0) b = 0;
                _glow[i] = ((uint)r << 16) | ((uint)g << 8) | (uint)b;
            }
            _glowReady = true;
        }

        /// <summary>Monochrome grain tile. Seeded once per strength, then scrolled by the
        /// frame offset, so a still frame cannot look like a fixed dither pattern.</summary>
        private sbyte[] BuildGrain(float amount)
        {
            if (_grainS == amount && _grainTab.Length == 16384) return _grainTab;
            if (_grainTab.Length != 16384) _grainTab = new sbyte[16384];
            uint s = 0x9E3779B9u;
            float k = amount * 46f;
            for (int i = 0; i < 16384; i++)
            {
                s ^= s << 13; s ^= s >> 17; s ^= s << 5;
                int v = (int)((s >> 24) & 0xFF) - 128;
                _grainTab[i] = (sbyte)(int)(v * k * 0.0078125f);
            }
            _grainS = amount;
            return _grainTab;
        }

        /// <summary>Two box-blur passes, separable, radius 1 and 3. Cheap because the
        /// plane is 1/64 of the frame; a gaussian would look the same here.</summary>
        private void Blur(float[] a, int w, int h)
        {
            int n = w > h ? w : h;
            if (_blurTmp == null || _blurTmp.Length < n) _blurTmp = new float[n];

            for (int pass = 0; pass < 2; pass++)
            {
                int rad = pass == 0 ? 1 : 3;
                for (int y = 0; y < h; y++)
                {
                    int baseI = y * w;
                    for (int x = 0; x < w; x++)
                    {
                        int x0 = x - rad; if (x0 < 0) x0 = 0;
                        int x1 = x + rad; if (x1 >= w) x1 = w - 1;
                        float s = 0f;
                        for (int k = x0; k <= x1; k++) s += a[baseI + k];
                        _blurTmp[x] = s / (x1 - x0 + 1);
                    }
                    for (int x = 0; x < w; x++) a[baseI + x] = _blurTmp[x];
                }
                for (int x = 0; x < w; x++)
                {
                    for (int y = 0; y < h; y++)
                    {
                        int y0 = y - rad; if (y0 < 0) y0 = 0;
                        int y1 = y + rad; if (y1 >= h) y1 = h - 1;
                        float s = 0f;
                        for (int k = y0; k <= y1; k++) s += a[k * w + x];
                        _blurTmp[y] = s / (y1 - y0 + 1);
                    }
                    for (int y = 0; y < h; y++) a[y * w + x] = _blurTmp[y];
                }
            }
        }
    }

    // ---------------------------------------------------------------- player window

    internal sealed class PlayerForm : Form
    {
        private Bitmap _bmp;
        private readonly object _gate = new object();
        private Point _lastMouse;
        private bool _haveMouse;
        private bool _closing;

        public PlayerForm(Bitmap initial)
        {
            _bmp = initial;
            FormBorderStyle = FormBorderStyle.None;
            StartPosition = FormStartPosition.Manual;
            WindowState = FormWindowState.Normal;
            BackColor = Color.Black;
            ShowInTaskbar = false;
            TopMost = true;
            DoubleBuffered = true;
            KeyPreview = true;
            Cursor.Hide();
            SetStyle(ControlStyles.AllPaintingInWmPaint | ControlStyles.Opaque | ControlStyles.UserPaint, true);
        }

        protected override void OnShown(EventArgs e)
        {
            base.OnShown(e);
            Rectangle b = Screen.PrimaryScreen.Bounds;
            Bounds = b;
            _lastMouse = Cursor.Position;
            _haveMouse = true;
        }

        /// <summary>
        /// Swaps in the next frame and returns the bitmap that is no longer displayed so
        /// the caller can reuse it. Full-screen frames are ~20 MB, so allocating one per
        /// frame at 24 fps churned ~500 MB/s through the large-object heap; the caller
        /// keeps a small ring instead. Safe because _gate is held, so no paint can be
        /// reading the retired bitmap once this returns.
        /// </summary>
        public Bitmap PostFrame(Bitmap b)
        {
            Bitmap old;
            lock (_gate)
            {
                old = _bmp;
                _bmp = b;
            }
            if (!_closing)
            {
                try { BeginInvoke(new MethodInvoker(Invalidate)); }
                catch (InvalidOperationException) { }
            }
            return ReferenceEquals(old, b) ? null : old;
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            lock (_gate)
            {
                if (_bmp == null)
                {
                    e.Graphics.Clear(Color.Black);
                    return;
                }
                Rectangle r = ClientRectangle;
                e.Graphics.Clear(Color.Black);
                // 1:1 when the bitmap already matches the window; otherwise a cheap
                // upscale. GDI+ bilinear to a 2880x1800 panel cost ~120 ms/frame and
                // throttled the loop to 6 fps, so nearest is the right trade here.
                e.Graphics.InterpolationMode = System.Drawing.Drawing2D.InterpolationMode.NearestNeighbor;
                e.Graphics.PixelOffsetMode = System.Drawing.Drawing2D.PixelOffsetMode.HighSpeed;
                e.Graphics.CompositingMode = System.Drawing.Drawing2D.CompositingMode.SourceCopy;
                double srcAspect = (double)_bmp.Width / _bmp.Height;
                double dstAspect = (double)r.Width / r.Height;
                Rectangle dest = r;
                if (dstAspect > srcAspect)
                {
                    // window is wider: fill height, crop sides
                    int w = (int)Math.Round(r.Height * srcAspect);
                    dest = new Rectangle((r.Width - w) / 2, 0, w, r.Height);
                }
                else
                {
                    int h = (int)Math.Round(r.Width / srcAspect);
                    dest = new Rectangle(0, (r.Height - h) / 2, r.Width, h);
                }
                e.Graphics.DrawImage(_bmp, dest);
            }
        }

        protected override void OnKeyDown(KeyEventArgs e)
        {
            base.OnKeyDown(e);
            RequestClose();
        }

        protected override void OnMouseDown(MouseEventArgs e)
        {
            base.OnMouseDown(e);
            RequestClose();
        }

        protected override void OnMouseMove(MouseEventArgs e)
        {
            base.OnMouseMove(e);
            if (!_haveMouse)
            {
                _lastMouse = Cursor.Position;
                _haveMouse = true;
                return;
            }
            Point p = Cursor.Position;
            int dx = Math.Abs(p.X - _lastMouse.X);
            int dy = Math.Abs(p.Y - _lastMouse.Y);
            if (dx + dy > 12) RequestClose();
        }

        private void RequestClose()
        {
            if (_closing) return;
            _closing = true;
            try { Cursor.Show(); } catch (Exception) { }
            Close();
        }

        protected override void OnFormClosing(FormClosingEventArgs e)
        {
            base.OnFormClosing(e);
            _closing = true;
            try { Cursor.Show(); } catch (Exception) { }
        }
    }

    // ---------------------------------------------------------------- program

    internal static class Program
    {
        private const string ResourceName = "smoke.mp4";

        [DllImport("kernel32.dll")]
        private static extern bool AttachConsole(int dwProcessId);

        // kernel32, not user32 - importing this from user32 threw
        // EntryPointNotFoundException on the first Play() and killed the player
        // before it drew a frame. It is also advisory: a display that refuses to
        // stay awake must never take the screensaver down with it.
        [DllImport("kernel32.dll")]
        private static extern uint SetThreadExecutionState(uint esFlags);

        private static void PreventSleep(bool on)
        {
            try
            {
                SetThreadExecutionState(on
                    ? ES_CONTINUOUS | ES_DISPLAY_REQUIRED | ES_SYSTEM_REQUIRED
                    : ES_CONTINUOUS);
            }
            catch (EntryPointNotFoundException) { }
            catch (DllNotFoundException) { }
        }

        [DllImport("user32.dll")]
        private static extern bool SetProcessDPIAware();

        private const uint ES_CONTINUOUS = 0x80000000;
        private const uint ES_DISPLAY_REQUIRED = 0x00000002;
        private const uint ES_SYSTEM_REQUIRED = 0x00000001;

        /// <summary>Console-subsystem output is not attached for a winexe, so reattach for CLI verbs.</summary>
        private static void AttachConsoleIfNeeded(string[] args)
        {
            bool want = false;
            for (int i = 0; i < args.Length; i++)
            {
                string a = args[i];
                if (a == "--selftest" || a == "--dump" || a == "--list-palettes" ||
                    a == "--help" || a == "-h" || a == "--bench" || a == "--export" ||
                    a == "--watch" || a == "--install-scr" || a == "--uninstall-scr" ||
                    a == "/c" || a == "-c") want = true;
            }
            if (!want) return;
            try
            {
                AttachConsole(-1);
                StreamWriter so = new StreamWriter(Console.OpenStandardOutput());
                so.AutoFlush = true;
                Console.SetOut(so);
                StreamWriter se = new StreamWriter(Console.OpenStandardError());
                se.AutoFlush = true;
                Console.SetError(se);
            }
            catch (Exception) { }
        }

        [STAThread]
        private static int Main(string[] args)
        {
            AttachConsoleIfNeeded(args);

            for (int i = 0; i < args.Length; i++)
            {
                if (args[i] == "--list-palettes") { ListPalettes(); return 0; }
                if (args[i] == "--help" || args[i] == "-h") { Help(); return 0; }
            }

            Options opt = Options.Parse(args);

            if (args.Length > 0 && args[0] == "--selftest") return SelfTest(opt);
            if (args.Length > 0 && args[0] == "--dump") return Dump(opt, args);
            if (args.Length > 0 && args[0] == "--bench") return Bench(opt, args);
            if (args.Length > 0 && args[0] == "--export") return Export(opt);
            if (args.Length > 0 && args[0] == "--export-all") return ExportAll(opt);
            if (args.Length > 0 && args[0] == "--watch") return Watch(opt);
            if (args.Length > 0 && args[0] == "--install-scr") return InstallScr(opt);
            if (args.Length > 0 && args[0] == "--uninstall-scr") return UninstallScr();

            // Windows starts a screen saver as: /s (run), /c (configure), /p <hwnd>
            // (preview). Git Bash rewrites a leading /path, so the -s spelling is
            // accepted too; both mean the same thing here.
            if (args.Length > 0 && (args[0] == "/c" || args[0] == "-c")) { Help(); return 0; }
            if (args.Length > 0 && (args[0] == "/p" || args[0] == "-p")) return 0;

            try { SetProcessDPIAware(); } catch (Exception) { }
            return Play(opt);
        }

        /// <summary>Times the per-frame grade so the render size can be tuned on this machine.</summary>
        private static int Bench(Options opt, string[] args)
        {
            int w = 1920, h = 1080, frames = 60;
            for (int i = 0; i < args.Length - 1; i++)
            {
                if (args[i] == "--render")
                {
                    Size s = ParseSize(args[i + 1], 1920, 1080);
                    w = s.Width; h = s.Height;
                }
                if (args[i] == "--frames") int.TryParse(args[i + 1], out frames);
            }

            Grade grade = BuildGrade(opt);
            Renderer rend = new Renderer(grade, opt, w, h);
            Bitmap bmp = new Bitmap(w, h, PixelFormat.Format32bppRgb);
            byte[] src = new byte[w * h * 4];
            Random rnd = new Random(7);
            rnd.NextBytes(src);

            rend.Blit(src, false, bmp, 1f, 0, 0, 0);      // warm up
            System.Diagnostics.Stopwatch sw = System.Diagnostics.Stopwatch.StartNew();
            for (int i = 0; i < frames; i++) rend.Blit(src, false, bmp, 1f, 0, 0, 0);
            sw.Stop();
            double ms = sw.Elapsed.TotalMilliseconds / frames;
            Console.WriteLine(string.Format(CultureInfo.InvariantCulture,
                "grade {0}  {1}x{2}  {3:F2} ms/frame  -> {4:F0} fps ceiling",
                grade.Name, w, h, ms, 1000.0 / ms));
            bmp.Dispose();
            return ms < 33.0 ? 0 : 1;
        }

        private static string AssetPath()
        {
            string dir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                                      "LumenRefresh");
            Directory.CreateDirectory(dir);
            return Path.Combine(dir, ResourceName);
        }

        /// <summary>Extracts the embedded footage once and returns its path.</summary>
        private static string EnsureAsset(bool verbose)
        {
            string path = AssetPath();
            Assembly asm = Assembly.GetExecutingAssembly();
            Stream rs = asm.GetManifestResourceStream(ResourceName);
            if (rs == null)
            {
                // development fallback: look next to the exe
                string local = Path.Combine(Path.GetDirectoryName(asm.Location), ResourceName);
                if (File.Exists(local)) return local;
                throw new InvalidOperationException("embedded asset missing: " + ResourceName);
            }
            long want;
            using (rs) { want = rs.Length; }

            if (File.Exists(path) && new FileInfo(path).Length == want)
            {
                if (verbose) Console.WriteLine("asset: cached " + path);
                return path;
            }

            Assembly asm2 = Assembly.GetExecutingAssembly();
            using (Stream s = asm2.GetManifestResourceStream(ResourceName))
            using (FileStream fs = new FileStream(path, FileMode.Create, FileAccess.Write, FileShare.None))
            {
                s.CopyTo(fs);
            }
            if (verbose) Console.WriteLine("asset: extracted " + path + " (" + new FileInfo(path).Length + " bytes)");
            return path;
        }

        private static Size ParseSize(string s, int dw, int dh)
        {
            if (!string.IsNullOrEmpty(s))
            {
                string[] parts = s.ToLowerInvariant().Split('x');
                if (parts.Length == 2)
                {
                    int w, h;
                    if (int.TryParse(parts[0], out w) && int.TryParse(parts[1], out h) && w > 0 && h > 0)
                        return new Size(w, h);
                }
            }
            return new Size(dw, dh);
        }

        private static Grade BuildGrade(Options opt)
        {
            string a, b;
            SplitPalette(opt.Palette, out a, out b);
            return BuildGrade(opt, a);
        }

        /// <summary>Splits "a+b" into the two halves of a palette blend. No '+' means a
        /// single static grade.</summary>
        private static void SplitPalette(string spec, out string a, out string b)
        {
            a = spec; b = null;
            if (spec == null) return;
            int plus = spec.IndexOf('+');
            if (plus > 0 && plus < spec.Length - 1)
            {
                a = spec.Substring(0, plus);
                b = spec.Substring(plus + 1);
            }
        }

        /// <summary>The far end of a "a+b" blend, or null for a single palette.</summary>
        private static Grade BuildBlendTo(Options opt)
        {
            string a, b;
            SplitPalette(opt.Palette, out a, out b);
            return b == null ? null : BuildGrade(opt, b);
        }

        private static Grade BuildGrade(Options opt, string palette)
        {
            Grade g = Grade.FromName(palette);
            if (!string.IsNullOrEmpty(opt.GradeSpec)) g.ApplySpec(opt.GradeSpec);
            if (opt.Pulse > 0) g.PulseAmount = opt.Pulse;
            if (!string.IsNullOrEmpty(opt.Duo)) g.ApplySpec("duo=" + opt.Duo);
            if (opt.Luma > 0) g.TargetLuma = opt.Luma;
            // --gamma rides on top of whatever the palette already asked for, so it can
            // be stacked onto a preset instead of replacing its curve.
            if (opt.Gamma > 0.01f && Math.Abs(opt.Gamma - 1f) > 0.0001f) g.Gamma *= opt.Gamma;
            g.Compile();
            return g;
        }

        /// <summary>Shifts a side in pixels to whole RGB triads, so a shift never lands
        /// red where green belongs and stripes the panel with colour fringes.</summary>
        private static int Triad(int px)
        {
            if (px <= 0) return 0;
            return (px / 3) * 3;
        }

        private static int Play(Options opt)
        {
            Grade fromGrade = BuildGrade(opt);
            Grade blendTo = BuildBlendTo(opt);
            // Progress ramp: two compiled grades, mixed by session time. The mix happens in
            // the baked tables, so the loop stays exactly as fast as a static grade.
            Grade toGrade = string.IsNullOrEmpty(opt.Progress) ? null : BuildGrade(opt, opt.Progress);
            Grade grade = fromGrade;
            double progressSpan = opt.ProgressMinutes > 0 ? opt.ProgressMinutes * 60.0 : 600.0;
            string asset = opt.Source != null ? opt.Source : EnsureAsset(opt.Verbose);

            Rectangle screen = Screen.PrimaryScreen.Bounds;
            Size target = ParseSize(opt.Render, 1920, 1080);
            if (target.Width > screen.Width) target.Width = screen.Width;
            if (target.Height > screen.Height) target.Height = screen.Height;
            // keep 16:9 so no distortion
            target.Height = (int)Math.Round(target.Width * 9.0 / 16.0);
            if (target.Height > screen.Height)
            {
                target.Height = screen.Height;
                target.Width = (int)Math.Round(target.Height * 16.0 / 9.0);
            }

            PreventSleep(true);

            // These MF interfaces are apartment-affine and the custom MF IIDs have no
            // cross-apartment marshaler, so a reader created on the STA UI thread cannot
            // be used from a worker - QueryInterface for IMFSourceReader fails with
            // E_NOINTERFACE and the player dies before drawing. Open, decode, grade and
            // dispose the source entirely on one MTA worker and hand the UI finished
            // bitmaps only. The placeholder is 16x9; the form cover-crops to the screen,
            // so its pixel size is cosmetic.
            Bitmap placeholder = new Bitmap(16, 9, PixelFormat.Format32bppRgb);
            PlayerForm form = new PlayerForm(placeholder);
            DateTime start = DateTime.UtcNow;
            bool stop = false;
            int rendered = 0;
            Dwell dwellRef = null;

            Thread worker = new Thread(delegate()
            {
                SmokeSource src = null;
                try
                {
                    src = SmokeSource.Open(asset, target.Width, target.Height);
                    int w = src.Width, h = src.Height;
                    Renderer rend = new Renderer(grade, opt, w, h);
                    if (blendTo != null) rend.SetBlendPair(blendTo);
                    int loopParity = 0;

                    // --heal needs a lit frame to hold before the first dip, and the clip
                    // opens on one. Decode past it once, then rewind to the real start.
                    Healer healer = null;
                    if (opt.Heal > 0.001f)
                    {
                        healer = new Healer(w, h, opt.Heal);
                        for (int i = 0; i < 48 && !healer.HaveHold; i++)
                        {
                            byte[] pf = src.Next();
                            if (pf == null) break;
                            healer.Feed(pf);
                        }
                        src.Rewind();
                    }

                    // Grade straight into panel-sized frames so the paint is a 1:1 copy.
                    // Scaling in GDI+ at paint time cost ~120 ms/frame at 2880x1800 and
                    // capped the loop near 6 fps; this sampler does it in the unsafe
                    // loop instead. Three buffers rotate through the form, which returns
                    // each retired one instead of disposing it.
                    int outW = screen.Width, outH = screen.Height;
                    Queue<Bitmap> spare = new Queue<Bitmap>();
                    for (int i = 0; i < 3; i++)
                        spare.Enqueue(new Bitmap(outW, outH, PixelFormat.Format32bppRgb));

                    Func<Bitmap> takeBuf = delegate()
                    {
                        return spare.Count > 0
                            ? spare.Dequeue()
                            : new Bitmap(outW, outH, PixelFormat.Format32bppRgb);
                    };
                    Action<Bitmap> giveBack = delegate(Bitmap b)
                    {
                        if (b == null) return;
                        if (b.Width == outW && b.Height == outH) spare.Enqueue(b);
                        else b.Dispose();
                    };

                    // Orbit / dwell: the cover-crop trims one axis, and that is exactly the
                    // room the window has to move in. Rotating those positions between loops
                    // means no column of the panel keeps receiving the same bright smoke.
                    Dwell dwell = (opt.Orbit && opt.Dwell) ? new Dwell() : null;
                    dwellRef = dwell;
                    Size dstSize = new Size(outW, outH);
                    int orbitQ = 0;
                    if (opt.Orbit)
                    {
                        orbitQ = opt.RotateQuadrant >= 0 ? ((opt.RotateQuadrant % 4) + 4) % 4 : 0;
                        rend.SetOrbitQuadrant(dstSize, orbitQ);
                    }
                    double doseSum = 0;
                    int doseN = 0, lastProgressSec = -1;

                    byte[] frame = src.Next();
                    if (frame != null && healer != null) frame = healer.Feed(frame);
                    if (frame != null)
                    {
                        Bitmap first = takeBuf();
                        rend.Blit(frame, src.BottomUp, first, 1f, 0, 0, 0);
                        giveBack(form.PostFrame(first));
                    }
                    DateTime loopStart = DateTime.UtcNow;
                    double frameInterval = 1.0 / 24.0 / Math.Max(0.05, opt.Speed);
                    int sinceKey = 0;
                    // Sleep only the time left in the frame, not a whole interval on top
                    // of the work - that turned a 41 ms budget into 41 ms + render time.
                    DateTime nextAt = DateTime.UtcNow;
                    while (!stop)
                    {
                        if (frame == null)
                        {
                            if (!opt.Loop) break;
                            // close the books on the loop that just finished, then hand the
                            // next one to the least-exercised position
                            if (dwell != null && doseN > 0) dwell.Add(orbitQ, doseSum / doseN);
                            doseSum = 0; doseN = 0;
                            src.Rewind();
                            frame = src.Next();
                            if (frame != null && healer != null) frame = healer.Feed(frame);
                            loopParity++;
                            loopStart = DateTime.UtcNow;
                            if (frame == null) break;
                            if (opt.Orbit)
                            {
                                orbitQ = dwell != null ? dwell.Next(orbitQ + 1) : orbitQ + 1;
                                rend.SetOrbitQuadrant(dstSize, orbitQ);
                            }
                        }

                        double elapsed = (DateTime.UtcNow - start).TotalSeconds;
                        if (toGrade != null && (int)elapsed != lastProgressSec)
                        {
                            lastProgressSec = (int)elapsed;
                            float pt = (float)Math.Min(1.0, elapsed / progressSpan);
                            rend.SetGrade(Grade.Blend(fromGrade, toGrade, pt));
                        }
                        if (dwell != null && (rendered % 24) == 0)
                        {
                            doseSum += MeanLuma(frame, src.Width, src.Height, 40);
                            doseN++;
                        }
                        float pulse = 1f;
                        if (grade.PulseAmount > 0)
                        {
                            double p = Math.Sin(elapsed * Math.PI * 2.0 * grade.PulseHz);
                            pulse = (float)(1.0 + p * grade.PulseAmount);
                        }

                        int shiftX = 0, shiftY = 0;
                        if (!opt.NoShift && opt.ShiftAmplitude > 0)
                        {
                            int phase = (int)(elapsed / 6.0) % 4;
                            int a = opt.ShiftAmplitude;
                            // A shift that is not a whole RGB triad lands red where green
                            // belongs and stripes the panel with colour fringes.
                            if (a > 0 && opt.TriadShift) a = Math.Max(3, Triad(a));
                            switch (phase)
                            {
                                case 0: shiftX = a; break;
                                case 1: shiftY = a; break;
                                case 2: shiftX = -a; break;
                                default: shiftY = -a; break;
                            }
                        }

                        Bitmap next = takeBuf();
                        rend.Time = rendered / 24f;
                        rend.Blit(frame, src.BottomUp, next, pulse, shiftX, shiftY, loopParity);
                        giveBack(form.PostFrame(next));
                        rendered++;

                        if (opt.Hud && sinceKey == 0)
                        {
                            // HUD text is drawn into the bitmap by the form; keep console simple
                        }
                        sinceKey++;

                        // trim the loop if requested
                        if (opt.SecondsPerLoop > 0 &&
                            (DateTime.UtcNow - loopStart).TotalSeconds >= opt.SecondsPerLoop)
                        {
                            src.Rewind();
                            loopParity++;
                            loopStart = DateTime.UtcNow;
                        }

                        if (opt.Minutes > 0 && (DateTime.UtcNow - start).TotalMinutes >= opt.Minutes) break;

                        nextAt = nextAt.AddMilliseconds(frameInterval * 1000.0);
                        double waitMs = (nextAt - DateTime.UtcNow).TotalMilliseconds;
                        if (waitMs > 0) Thread.Sleep((int)waitMs);
                        else if (waitMs < -1000) nextAt = DateTime.UtcNow;  // fell behind; resync
                        frame = src.Next();
                        if (frame != null && healer != null) frame = healer.Feed(frame);
                    }
                }
                catch (Exception ex)
                {
                    Console.Error.WriteLine("decode unavailable: " + ex.Message);
                    Console.Error.WriteLine("run with --dump to grade frames offline instead");
                }
                finally
                {
                    if (src != null) { try { src.Dispose(); } catch (Exception) { } }
                    stop = true;
                    try { form.BeginInvoke(new MethodInvoker(delegate() { form.Close(); })); }
                    catch (Exception) { }
                }
            });
            worker.IsBackground = true;
            worker.SetApartmentState(ApartmentState.MTA);

            form.Shown += delegate(object sender, EventArgs e) { worker.Start(); };
            Application.Run(form);

            stop = true;
            try { worker.Join(2000); } catch (Exception) { }
            PreventSleep(false);
            if (dwellRef != null) dwellRef.Report();
            Console.Error.WriteLine("frames drawn: " + rendered
                + " (" + (DateTime.UtcNow - start).TotalSeconds.ToString("0.0") + " s)");
            return 0;        }

        private static int Dump(Options opt, string[] args)
        {
            string outDir = args.Length > 1 && !args[1].StartsWith("--") ? args[1] : "frames";
            Directory.CreateDirectory(outDir);
            List<double> times = new List<double>();
            for (int i = 0; i < args.Length - 1; i++)
            {
                if (args[i] == "--times")
                {
                    string[] parts = args[i + 1].Split(',');
                    for (int k = 0; k < parts.Length; k++)
                    {
                        double t;
                        if (double.TryParse(parts[k], NumberStyles.Float, CultureInfo.InvariantCulture, out t))
                            times.Add(t);
                    }
                }
            }
            if (times.Count == 0) { times.Add(2); times.Add(18); times.Add(34); times.Add(50); }

            Grade grade = BuildGrade(opt);
            Grade blendTo = BuildBlendTo(opt);
            string asset = opt.Source != null ? opt.Source : EnsureAsset(opt.Verbose);

            SmokeSource src;
            try { src = SmokeSource.Open(asset, 960, 540); }
            catch (Exception ex)
            {
                Console.Error.WriteLine("decode unavailable: " + ex.Message);
                return 2;
            }

            Renderer rend = new Renderer(grade, opt, src.Width, src.Height);
            if (blendTo != null) rend.SetBlendPair(blendTo);
            int w = src.Width, h = src.Height;
            int frameIndex = 0;
            double frameTime = 1.0 / 24.0;
            int made = 0;

            times.Sort();
            int ti = 0;
            byte[] frame = src.Next();
            while (frame != null && ti < times.Count)
            {
                double t = frameIndex * frameTime;
                if (t + 1e-9 >= times[ti])
                {
                    Bitmap bmp = new Bitmap(w, h, PixelFormat.Format32bppRgb);
                    rend.Time = (float)(frameIndex * frameTime);
                    rend.Blit(frame, src.BottomUp, bmp, 1f, 0, 0, 0);
                    string name = Path.Combine(outDir, string.Format(CultureInfo.InvariantCulture,
                        "{0}_t{1:00}.png", grade.Name, (int)times[ti]));
                    bmp.Save(name, ImageFormat.Png);
                    bmp.Dispose();
                    Console.WriteLine("wrote " + name + "  " + w + "x" + h);
                    made++;
                    ti++;
                }
                frameIndex++;
                if (ti >= times.Count) break;
                frame = src.Next();
                if (frame == null && opt.Loop) { src.Rewind(); frame = src.Next(); }
            }
            src.Dispose();
            return made > 0 ? 0 : 1;
        }

        private static int Sum(Color c) { return c.R + c.G + c.B; }

        /// <summary>Mean luminance of a decoded frame, sampled with a stride. Used by the
        /// dwell accountant; a full-frame pass would cost more than the blit.</summary>
        private static double MeanLuma(byte[] f, int w, int h, int stride)
        {
            if (stride < 1) stride = 1;
            long sum = 0;
            int n = 0;
            for (int y = 0; y < h; y += stride)
            {
                int row = y * w * 4;
                for (int x = 0; x < w; x += stride)
                {
                    int i = row + x * 4;
                    sum += (f[i] * 29 + f[i + 1] * 150 + f[i + 2] * 77) >> 8;
                    n++;
                }
            }
            return n == 0 ? 0.0 : (double)sum / n;
        }

        // ------------------------------------------------------------ video export

        private static string FindFfmpeg(string given)
        {
            if (!string.IsNullOrEmpty(given))
                return File.Exists(given) ? given : null;

            string path = Environment.GetEnvironmentVariable("PATH") ?? "";
            string[] dirs = path.Split(';');
            for (int i = 0; i < dirs.Length; i++)
            {
                if (dirs[i].Length == 0) continue;
                try
                {
                    string c = Path.Combine(dirs[i], "ffmpeg.exe");
                    if (File.Exists(c)) return c;
                }
                catch (Exception) { }
            }
            return null;
        }

        /// <summary>
        /// Renders the loop to a video by piping raw BGRA frames into ffmpeg. This is the
        /// same sampler that feeds the screen, so the file shows exactly what the panel
        /// shows - no separate rendering path to drift.
        /// </summary>
        private static int Export(Options opt)
        {
            string ff = FindFfmpeg(opt.Ffmpeg);
            if (ff == null)
            {
                Console.Error.WriteLine("ffmpeg not found - pass --ffmpeg <path to ffmpeg.exe>");
                return 2;
            }

            string asset = opt.Source != null ? opt.Source : EnsureAsset(opt.Verbose);
            Size sz = ParseSize(opt.ExportSize, 1920, 1080);
            int w = sz.Width, h = (int)Math.Round(sz.Width * 9.0 / 16.0);
            double seconds = opt.ExportSeconds > 0 ? opt.ExportSeconds : 60;
            int total = (int)Math.Round(seconds * 24.0);

            SmokeSource src;
            try { src = SmokeSource.Open(asset, w, h); }
            catch (Exception ex)
            {
                Console.Error.WriteLine("decode unavailable: " + ex.Message);
                return 2;
            }

            Grade fromGrade = BuildGrade(opt);
            Grade toGrade = string.IsNullOrEmpty(opt.Progress) ? null : BuildGrade(opt, opt.Progress);
            Grade blendTo = BuildBlendTo(opt);
            double progressSpan = opt.ProgressMinutes > 0 ? opt.ProgressMinutes * 60.0 : 600.0;
            Renderer rend = new Renderer(fromGrade, opt, src.Width, src.Height);
            if (blendTo != null) rend.SetBlendPair(blendTo);

            Healer healer = null;
            if (opt.Heal > 0.001f)
            {
                healer = new Healer(src.Width, src.Height, opt.Heal);
                for (int i = 0; i < 48 && !healer.HaveHold; i++)
                {
                    byte[] pf = src.Next();
                    if (pf == null) break;
                    healer.Feed(pf);
                }
                src.Rewind();
            }

            string outPath = Path.GetFullPath(opt.Export);
            ProcessStartInfo psi = new ProcessStartInfo(ff);
            psi.Arguments = string.Format(CultureInfo.InvariantCulture,
                "-y -hide_banner -loglevel error -f rawvideo -pixel_format bgra -video_size {0}x{1} " +
                "-framerate 24 -i - -an -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p " +
                "-movflags +faststart \"{2}\"", w, h, outPath);
            psi.UseShellExecute = false;
            psi.RedirectStandardInput = true;
            psi.CreateNoWindow = true;

            Process ffProc;
            try { ffProc = Process.Start(psi); }
            catch (Exception ex) { Console.Error.WriteLine("ffmpeg failed to start: " + ex.Message); return 2; }

            int wrote = 0;
            try
            {
                Stream stdin = ffProc.StandardInput.BaseStream;
                Bitmap bmp = new Bitmap(w, h, PixelFormat.Format32bppRgb);
                byte[] row = new byte[w * 4];
                byte[] frame = src.Next();
                if (frame != null && healer != null) frame = healer.Feed(frame);
                for (int i = 0; i < total && frame != null; i++)
                {
                    if (toGrade != null)
                    {
                        double t = (double)i / 24.0 / progressSpan;
                        rend.SetGrade(Grade.Blend(fromGrade, toGrade, (float)Math.Min(1.0, t)));
                    }
                    rend.Time = i / 24f;
                    rend.Blit(frame, src.BottomUp, bmp, 1f, 0, 0, i / 1440);

                    BitmapData bd = bmp.LockBits(new Rectangle(0, 0, w, h),
                                                 ImageLockMode.ReadOnly, PixelFormat.Format32bppRgb);
                    try
                    {
                        IntPtr p = bd.Scan0;
                        int stride = bd.Stride;
                        for (int y = 0; y < h; y++)
                        {
                            Marshal.Copy(new IntPtr(p.ToInt64() + (long)y * stride), row, 0, w * 4);
                            stdin.Write(row, 0, row.Length);
                        }
                    }
                    finally { bmp.UnlockBits(bd); }

                    wrote++;
                    if ((i % 120) == 0) Console.Error.WriteLine("  " + i + "/" + total + " frames");

                    frame = src.Next();
                    if (frame == null && opt.Loop)
                    {
                        src.Rewind();
                        frame = src.Next();
                    }
                    if (frame != null && healer != null) frame = healer.Feed(frame);
                }
                bmp.Dispose();
                stdin.Flush();
                stdin.Close();
            }
            finally
            {
                src.Dispose();
            }

            ffProc.WaitForExit();
            int code = ffProc.ExitCode;
            ffProc.Dispose();
            if (code != 0)
            {
                Console.Error.WriteLine("ffmpeg exited " + code + " - no file written");
                return 3;
            }
            Console.WriteLine("wrote " + outPath + "  " + w + "x" + h + "  " + wrote + " frames  " +
                              (wrote / 24.0).ToString("0.0", CultureInfo.InvariantCulture) + " s");
            return 0;
        }

        /// <summary>
        /// One clip per palette. Each palette reopens the source, so a failure on one
        /// cannot take the batch down, and an existing file is skipped rather than
        /// re-encoded - that is what makes an interrupted 42-palette run resumable.
        /// </summary>
        private static int ExportAll(Options opt)
        {
            string dir;
            try
            {
                dir = Path.GetFullPath(opt.ExportAll);
                Directory.CreateDirectory(dir);
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("bad --export-all directory: " + ex.Message);
                return 2;
            }

            List<string> names = new List<string>();
            if (!string.IsNullOrEmpty(opt.Palettes))
            {
                string[] parts = opt.Palettes.Split(',');
                for (int k = 0; k < parts.Length; k++)
                {
                    string n = parts[k].Trim();
                    if (n.Length > 0) names.Add(n);
                }
            }
            else
            {
                string[] all = new string[Grade.Presets.Count];
                Grade.Presets.Keys.CopyTo(all, 0);
                Array.Sort(all);
                for (int k = 0; k < all.Length; k++) names.Add(all[k]);
            }
            if (names.Count == 0) { Console.Error.WriteLine("no palettes to export"); return 2; }

            Console.Error.WriteLine("exporting " + names.Count + " palette(s) into " + dir);
            int ok = 0, failed = 0;
            for (int i = 0; i < names.Count; i++)
            {
                string name = names[i];
                string file = Path.Combine(dir, name + ".mp4");
                if (File.Exists(file))
                {
                    Console.Error.WriteLine("  [" + (i + 1) + "/" + names.Count + "] " + name + "  exists, skipped");
                    ok++;
                    continue;
                }
                Console.Error.WriteLine("  [" + (i + 1) + "/" + names.Count + "] " + name);
                Options one = opt;
                one.Palette = name;
                one.Palettes = null;
                one.ExportAll = null;
                one.Export = file;
                try
                {
                    int rc = Export(one);
                    if (rc == 0) ok++;
                    else { failed++; Console.Error.WriteLine("  " + name + " failed (rc=" + rc + ")"); }
                }
                catch (Exception ex)
                {
                    failed++;
                    Console.Error.WriteLine("  " + name + " failed: " + ex.Message);
                }
            }
            Console.WriteLine("batch: " + ok + " ok, " + failed + " failed, into " + dir);
            return failed == 0 ? 0 : 3;
        }

        // ------------------------------------------------------- shell integration

        private static string ScrPath()
        {
            string dir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                                      "LumenRefresh");
            Directory.CreateDirectory(dir);
            return Path.Combine(dir, "LumenRefresh.scr");
        }

        /// <summary>Registers this exe as the current user's screen saver. HKCU only, and
        /// undone by --uninstall-scr, so nothing machine-wide is touched.</summary>
        private static int InstallScr(Options opt)
        {
            string exe = Assembly.GetExecutingAssembly().Location;
            string scr = ScrPath();
            try
            {
                if (!string.Equals(Path.GetFullPath(exe), Path.GetFullPath(scr), StringComparison.OrdinalIgnoreCase))
                    File.Copy(exe, scr, true);
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("cannot copy to " + scr + ": " + ex.Message);
                return 2;
            }

            try
            {
                using (RegistryKey k = Registry.CurrentUser.OpenSubKey(@"Control Panel\Desktop", true))
                {
                    if (k == null)
                    {
                        Console.Error.WriteLine(@"cannot open HKCU\Control Panel\Desktop");
                        return 2;
                    }
                    k.SetValue("SCRNSAVE.EXE", scr, RegistryValueKind.String);
                    k.SetValue("ScreenSaveActive", "1", RegistryValueKind.String);
                    if (opt.ScrTimeout > 0)
                        k.SetValue("ScreenSaveTimeOut", opt.ScrTimeout.ToString(CultureInfo.InvariantCulture),
                                   RegistryValueKind.String);
                }
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("registry write failed: " + ex.Message);
                return 2;
            }

            Console.WriteLine("screen saver installed: " + scr);
            if (opt.ScrTimeout > 0) Console.WriteLine("  idle timeout: " + opt.ScrTimeout + " s");
            Console.WriteLine("  undo with: LumenRefresh.exe --uninstall-scr");
            return 0;
        }

        private static int UninstallScr()
        {
            try
            {
                using (RegistryKey k = Registry.CurrentUser.OpenSubKey(@"Control Panel\Desktop", true))
                {
                    if (k == null) return 2;
                    k.SetValue("SCRNSAVE.EXE", "", RegistryValueKind.String);
                    k.SetValue("ScreenSaveActive", "0", RegistryValueKind.String);
                }
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("registry write failed: " + ex.Message);
                return 2;
            }
            Console.WriteLine("screen saver cleared (HKCU only; the .scr file is left in place)");
            return 0;
        }

        // ------------------------------------------------------------ idle trigger

        [StructLayout(LayoutKind.Sequential)]
        private struct LASTINPUTINFO
        {
            public uint cbSize;
            public uint dwTime;
        }

        [DllImport("user32.dll")]
        private static extern bool GetLastInputInfo(ref LASTINPUTINFO plii);

        private static uint IdleSeconds()
        {
            LASTINPUTINFO lii = new LASTINPUTINFO();
            lii.cbSize = (uint)Marshal.SizeOf(typeof(LASTINPUTINFO));
            if (!GetLastInputInfo(ref lii)) return 0;
            return unchecked((uint)Environment.TickCount - lii.dwTime) / 1000u;
        }

        /// <summary>Runs the refresh whenever the machine has been idle for N seconds,
        /// then waits for real input before arming again. Not a screen saver: nothing is
        /// locked or hidden, the routine just plays on top of whatever is showing.</summary>
        private static int Watch(Options opt)
        {
            int threshold = opt.IdleSeconds > 0 ? opt.IdleSeconds : 120;
            Console.Error.WriteLine("watching for idle: starting after " + threshold + " s, Ctrl+C to stop");
            while (true)
            {
                if (IdleSeconds() >= (uint)threshold)
                {
                    Console.Error.WriteLine("idle reached - starting refresh");
                    Play(opt);
                    // Do not relaunch straight away: the session just ended because the
                    // user touched the machine, but TickCount can still report idle 0..1.
                    while (IdleSeconds() < 2) Thread.Sleep(500);
                }
                Thread.Sleep(1000);
            }
        }



        private static int SelfTest(Options opt)
        {
            int failures = 0;

            // 1. the grade must not collapse into a single channel
            string[] palettes = new string[] { "native", "ember", "teal", "magma", "ice", "violet", "lime",
                                               "ruby", "amber", "mono", "thermal", "ash", "venom", "neon",
                                               "prism", "duo-cyan", "duo-violet", "duo-blood", "duo-sun",
                                               "solaris", "deepsea", "toxic", "rose",
                                               "neon-cyan", "neon-pink", "neon-lime",
                                               "fluoro-sun", "fluoro-mint", "fluoro-violet",
                                               "pastel", "pastel-mint", "pastel-rose",
                                               "electric", "elec-violet",
                                               "sunset", "sunset-clouds", "yt-blue", "yt-deep" };
            for (int i = 0; i < palettes.Length; i++)
            {
                Grade g = Grade.FromName(palettes[i]);
                g.Compile();
                if (g.Ramp != null)
                {
                    // ramp grades deliberately collapse chroma; the property that must hold
                    // is that they still respond monotonically to luminance.
                    int a = Sum(g.Map(0, 0, 0, 1f));
                    int b = Sum(g.Map(128, 128, 128, 1f));
                    int c = Sum(g.Map(255, 255, 255, 1f));
                    bool rampOk = a < b && b < c;
                    Console.WriteLine((rampOk ? "PASS" : "FAIL") + "  palette " + palettes[i] +
                                      " maps luminance monotonically (" + a + "<" + b + "<" + c + ")");
                    if (!rampOk) failures++;
                }
                else
                {
                    Color c1 = g.Map(200, 60, 40, 1f);
                    Color c2 = g.Map(40, 120, 200, 1f);
                    int d = Math.Abs(c1.R - c2.R) + Math.Abs(c1.G - c2.G) + Math.Abs(c1.B - c2.B);
                    bool ok = d > 20;
                    Console.WriteLine((ok ? "PASS" : "FAIL") + "  palette " + palettes[i] +
                                      " separates two inks (delta=" + d + ")");
                    if (!ok) failures++;

                    int lit = c1.R + c1.G + c1.B;
                    bool bright = lit > 30;
                    Console.WriteLine((bright ? "PASS" : "FAIL") + "  palette " + palettes[i] +
                                      " keeps ink visible (sum=" + lit + ")");
                    if (!bright) failures++;
                }
            }

            // 2. mono must neutralise chroma
            Grade mono = Grade.FromName("mono");
            mono.Compile();
            Color m1 = mono.Map(220, 30, 30, 1f);
            bool neut = Math.Abs(m1.R - m1.G) <= 6 && Math.Abs(m1.G - m1.B) <= 6;
            Console.WriteLine((neut ? "PASS" : "FAIL") + "  mono is neutral (" + m1.R + "," + m1.G + "," + m1.B + ")");
            if (!neut) failures++;

            // 2b. a duotone must put the two dyes on two different colours, not on one
            // hue - that is the whole point of the two-ink mode.
            Grade dc = Grade.FromName("duo-cyan");
            dc.Compile();
            Color coolInk = dc.Map(80, 0, 200, 1f);
            Color warmInk = dc.Map(80, 200, 0, 1f);
            bool duoOk = (coolInk.B - coolInk.R) > 40 && (warmInk.R - warmInk.B) > 40;
            Console.WriteLine((duoOk ? "PASS" : "FAIL") + "  duotone keeps two inks apart (" +
                              coolInk.R + "," + coolInk.G + "," + coolInk.B + " vs " +
                              warmInk.R + "," + warmInk.G + "," + warmInk.B + ")");
            if (!duoOk) failures++;

            // 2c. dose target: mid grey must land near the requested mean luminance
            Grade dose = Grade.FromName("native");
            dose.TargetLuma = 0.5f;
            dose.Compile();
            Color mid = dose.Map(128, 128, 128, 1f);
            double midY = (0.213 * mid.R + 0.715 * mid.G + 0.072 * mid.B) / 255.0;
            bool doseOk = midY > 0.35 && midY < 0.65;
            Console.WriteLine((doseOk ? "PASS" : "FAIL") + "  luma target lands mid grey near 0.50 (" +
                              midY.ToString("0.000", CultureInfo.InvariantCulture) + ")");
            if (!doseOk) failures++;

            // 2d. triad rounding: a shift must never break an RGB triad
            bool triadOk = Triad(9) == 9 && Triad(7) == 6 && Triad(2) == 0;
            Console.WriteLine((triadOk ? "PASS" : "FAIL") + "  pixel shift rounds to whole triads");
            if (!triadOk) failures++;

            // 2e. progress blend must be linear in the baked tables
            Grade mixA = Grade.FromName("ruby"); mixA.Compile();
            Grade mixB = Grade.FromName("ice"); mixB.Compile();
            Grade half = Grade.Blend(mixA, mixB, 0.5f);
            Color ea = mixA.Map(128, 128, 128, 1f), eb = mixB.Map(128, 128, 128, 1f);
            Color em = half.Map(128, 128, 128, 1f);
            int errR = Math.Abs(em.R - (ea.R + eb.R) / 2);
            int errG = Math.Abs(em.G - (ea.G + eb.G) / 2);
            int errB = Math.Abs(em.B - (ea.B + eb.B) / 2);
            bool blendOk = errR <= 3 && errG <= 3 && errB <= 3;
            Console.WriteLine((blendOk ? "PASS" : "FAIL") + "  progress blend is linear (err " +
                              errR + "," + errG + "," + errB + ")");
            if (!blendOk) failures++;

            // 2f. orbit must actually have room on this panel and none at position 0
            Renderer orb = new Renderer(mixA, opt, 1920, 1080);
            orb.SetOrbitQuadrant(new Size(2880, 1800), 1);
            float roomX = orb.OrbitX;
            orb.SetOrbitQuadrant(new Size(2880, 1800), 0);
            bool orbitOk = roomX > 1f && orb.OrbitX == 0f;
            Console.WriteLine((orbitOk ? "PASS" : "FAIL") + "  orbit has room to move (" +
                              roomX.ToString("0.0", CultureInfo.InvariantCulture) + " px)");
            if (!orbitOk) failures++;

            // 2g. effects: each must move the frame, and in the right direction
            {
                int ew = 160, eh = 90;
                byte[] ef = new byte[ew * eh * 4];
                for (int i = 0; i < ew * eh; i++)
                {
                    int x = i % ew, y = i / ew;
                    int b = 40, g = 24, r = 16;                          // dim ground
                    int dx = x - 80, dy = y - 45;
                    if (dx * dx + dy * dy < 260) { b = 210; g = 200; r = 190; }   // bright blob
                    ef[i * 4] = (byte)b; ef[i * 4 + 1] = (byte)g; ef[i * 4 + 2] = (byte)r; ef[i * 4 + 3] = 255;
                }

                Grade eg = Grade.FromName("mono");
                eg.Compile();

                Options eo = new Options(); eo.Palette = "mono";

                Renderer rb2 = new Renderer(eg, eo, ew, eh);
                Bitmap plainB = new Bitmap(ew, eh, PixelFormat.Format32bppRgb);
                rb2.Time = 0.7f;
                rb2.Blit(ef, false, plainB, 1f, 0, 0, 0);

                Options eoR = new Options(); eoR.Palette = "mono"; eoR.Ripple = 14f;
                Renderer rr2 = new Renderer(eg, eoR, ew, eh);
                Bitmap ripB = new Bitmap(ew, eh, PixelFormat.Format32bppRgb);
                rr2.Time = 0.7f;
                rr2.Blit(ef, false, ripB, 1f, 0, 0, 0);
                int moved = 0;
                for (int y = 0; y < eh; y++)
                    for (int x = 0; x < ew; x++)
                        if (plainB.GetPixel(x, y).ToArgb() != ripB.GetPixel(x, y).ToArgb()) moved++;
                bool rippleOk = moved > 500;
                Console.WriteLine((rippleOk ? "PASS" : "FAIL") + "  ripple displaces the frame (" + moved + " px)");
                if (!rippleOk) failures++;

                Options eoS = new Options(); eoS.Palette = "mono"; eoS.Scan = 1f;
                Renderer sr2 = new Renderer(eg, eoS, ew, eh);
                Bitmap scanB = new Bitmap(ew, eh, PixelFormat.Format32bppRgb);
                sr2.Blit(ef, false, scanB, 1f, 0, 0, 0);

                Options eoB = new Options(); eoB.Palette = "mono"; eoB.Bloom = 0.9f;
                Renderer br2 = new Renderer(eg, eoB, ew, eh);
                Bitmap glowB = new Bitmap(ew, eh, PixelFormat.Format32bppRgb);
                br2.Blit(ef, false, glowB, 1f, 0, 0, 0);   // seeds the glow buffer
                br2.Blit(ef, false, glowB, 1f, 0, 0, 0);   // and this frame adds it back

                long pPlain = 0, pScan = 0, pGlow = 0;
                for (int y = 0; y < eh; y++)
                {
                    for (int x = 0; x < ew; x++)
                    {
                        Color cp = plainB.GetPixel(x, y), cs = scanB.GetPixel(x, y), cg = glowB.GetPixel(x, y);
                        pPlain += (cp.R * 77 + cp.G * 150 + cp.B * 29) >> 8;
                        pScan += (cs.R * 77 + cs.G * 150 + cs.B * 29) >> 8;
                        pGlow += (cg.R * 77 + cg.G * 150 + cg.B * 29) >> 8;
                    }
                }
                // scan must darken, but a little: it is a texture, not a dimmer
                bool scanOk = pScan < pPlain * 95 / 100 && pScan > pPlain * 60 / 100;
                Console.WriteLine((scanOk ? "PASS" : "FAIL") + "  scan darkens without dimming (" +
                                  (pScan * 100 / pPlain) + "% of plain)");
                if (!scanOk) failures++;

                // bloom must add light, without clipping the frame to white
                bool bloomOk = pGlow > pPlain * 102 / 100 && pGlow < pPlain * 300 / 100;
                Console.WriteLine((bloomOk ? "PASS" : "FAIL") + "  bloom adds glow without washing out (" +
                                  (pGlow * 100 / pPlain) + "% of plain)");
                if (!bloomOk) failures++;

                plainB.Dispose(); ripB.Dispose(); scanB.Dispose(); glowB.Dispose();
            }

            // 2h. --gamma must lift the midtones without moving black
            {
                Options gm1 = new Options(); gm1.Palette = "native";
                Options gm2 = new Options(); gm2.Palette = "native"; gm2.Gamma = 1.8f;
                int gv1 = BuildGrade(gm1).Map(96, 96, 96, 1f).R;
                int gv2 = BuildGrade(gm2).Map(96, 96, 96, 1f).R;
                int gv0 = BuildGrade(gm2).Map(0, 0, 0, 1f).R;
                bool gammaOk = gv2 > gv1 + 8 && gv0 < 4;
                Console.WriteLine((gammaOk ? "PASS" : "FAIL") + "  gamma lifts midtones only (" +
                                  gv1 + " -> " + gv2 + ", black " + gv0 + ")");
                if (!gammaOk) failures++;
            }

            // 2i. --grain must perturb the frame, and roughly preserve its mean
            {
                int nw = 160, nh = 90;
                byte[] nf = new byte[nw * nh * 4];
                for (int i = 0; i < nw * nh; i++)
                {
                    nf[i * 4] = 90; nf[i * 4 + 1] = 90; nf[i * 4 + 2] = 90; nf[i * 4 + 3] = 255;
                }
                Grade ng = Grade.FromName("native"); ng.Compile();
                Options no0 = new Options(); no0.Palette = "native";
                Options no1 = new Options(); no1.Palette = "native"; no1.Grain = 1f;
                Bitmap nb0 = new Bitmap(nw, nh, PixelFormat.Format32bppRgb);
                Bitmap nb1 = new Bitmap(nw, nh, PixelFormat.Format32bppRgb);
                Renderer nr0 = new Renderer(ng, no0, nw, nh);
                Renderer nr1 = new Renderer(ng, no1, nw, nh);
                nr0.Time = 0f; nr0.Blit(nf, false, nb0, 1f, 0, 0, 0);
                nr1.Time = 0f; nr1.Blit(nf, false, nb1, 1f, 0, 0, 0);
                int nchanged = 0;
                long nsum0 = 0, nsum1 = 0;
                for (int y = 0; y < nh; y++)
                {
                    for (int x = 0; x < nw; x++)
                    {
                        int a0 = nb0.GetPixel(x, y).R, a1 = nb1.GetPixel(x, y).R;
                        if (a0 != a1) nchanged++;
                        nsum0 += a0; nsum1 += a1;
                    }
                }
                int npx = nw * nh;
                long nBias = nsum1 - nsum0;
                bool grainOk = nchanged > npx / 2 && Math.Abs(nBias) < npx * 2;
                Console.WriteLine((grainOk ? "PASS" : "FAIL") + "  grain perturbs " +
                                  (nchanged * 100 / npx) + "% of pixels, mean drift " +
                                  (nBias / (double)npx).ToString("0.00", CultureInfo.InvariantCulture));
                if (!grainOk) failures++;
                nb0.Dispose(); nb1.Dispose();
            }

            // 2j. an a+b blend must sweep, and must meet itself at the loop seam
            {
                int sw2 = 64, sh2 = 36;
                byte[] sf = new byte[sw2 * sh2 * 4];
                for (int i = 0; i < sw2 * sh2; i++)
                {
                    sf[i * 4] = 150; sf[i * 4 + 1] = 120; sf[i * 4 + 2] = 100; sf[i * 4 + 3] = 255;
                }
                Grade sga = Grade.FromName("ember"); sga.Compile();
                Grade sgb = Grade.FromName("ice"); sgb.Compile();
                Options so = new Options(); so.Palette = "ember+ice"; so.BlendPeriod = 60f;
                Renderer sr = new Renderer(sga, so, sw2, sh2);
                sr.SetBlendPair(sgb);
                Bitmap sb0 = new Bitmap(sw2, sh2, PixelFormat.Format32bppRgb);
                Bitmap sbm = new Bitmap(sw2, sh2, PixelFormat.Format32bppRgb);
                Bitmap sb1 = new Bitmap(sw2, sh2, PixelFormat.Format32bppRgb);
                sr.Time = 0f; sr.Blit(sf, false, sb0, 1f, 0, 0, 0);
                sr.Time = 30f; sr.Blit(sf, false, sbm, 1f, 0, 0, 0);
                sr.Time = 59.9f; sr.Blit(sf, false, sb1, 1f, 0, 0, 0);
                Color sc0 = sb0.GetPixel(32, 18), scm = sbm.GetPixel(32, 18), sc1 = sb1.GetPixel(32, 18);
                int seamGap = Math.Abs(sc0.R - sc1.R) + Math.Abs(sc0.G - sc1.G) + Math.Abs(sc0.B - sc1.B);
                int swing = Math.Abs(sc0.R - scm.R) + Math.Abs(sc0.G - scm.G) + Math.Abs(sc0.B - scm.B);
                bool sweepOk = seamGap <= 6 && swing > 20;
                Console.WriteLine((sweepOk ? "PASS" : "FAIL") + "  palette blend sweeps (" + swing +
                                  ") and closes the seam (" + seamGap + ")");
                if (!sweepOk) failures++;
                sb0.Dispose(); sbm.Dispose(); sb1.Dispose();
            }

            // 2j-b. a ramp palette and a duo palette must crossfade. Mixing only the ramp
            // tables returned grade A here, so the sweep above (two hue/sat palettes)
            // passed while "neon-cyan+sunset-clouds" rendered as plain neon-cyan.
            {
                Grade xa = Grade.FromName("neon-cyan"); xa.Compile();
                Grade xb = Grade.FromName("sunset-clouds"); xb.Compile();
                Grade xEnd = Grade.Blend(xa, xb, 1f);
                Grade xMid = Grade.Blend(xa, xb, 0.4f);
                int[] qR = { 40, 120, 200, 90 };
                int[] qG = { 60, 90, 200, 30 };
                int[] qB = { 80, 40, 30, 210 };
                int dToB = 0, dFromA = 0, dToA = 0;
                for (int q = 0; q < 4; q++)
                {
                    Color cb = xb.Map(qR[q], qG[q], qB[q], 1f);
                    Color ca = xa.Map(qR[q], qG[q], qB[q], 1f);
                    Color ce = xEnd.Map(qR[q], qG[q], qB[q], 1f);
                    Color cm = xMid.Map(qR[q], qG[q], qB[q], 1f);
                    dToB += Math.Abs(ce.R - cb.R) + Math.Abs(ce.G - cb.G) + Math.Abs(ce.B - cb.B);
                    dToA += Math.Abs(ce.R - ca.R) + Math.Abs(ce.G - ca.G) + Math.Abs(ce.B - ca.B);
                    dFromA += Math.Abs(cm.R - ca.R) + Math.Abs(cm.G - ca.G) + Math.Abs(cm.B - ca.B);
                }
                bool mixOk = dToB <= 2 && dFromA > 30 && dToA > 30;
                Console.WriteLine((mixOk ? "PASS" : "FAIL") + "  ramp and duo crossfade (ends on B: " +
                                  dToB + ", mid moved from A: " + dFromA + ")");
                if (!mixOk) failures++;
            }

            // 2k. --heal must pass a lit frame through and cover a black gap with the hold
            {
                int hw2 = 96, hh2 = 54;
                byte[] lit = new byte[hw2 * hh2 * 4];
                for (int i = 0; i < hw2 * hh2; i++)
                {
                    lit[i * 4] = 60; lit[i * 4 + 1] = 120; lit[i * 4 + 2] = 180; lit[i * 4 + 3] = 255;
                }
                byte[] blk = new byte[hw2 * hh2 * 4];
                for (int i = 0; i < hw2 * hh2; i++) blk[i * 4 + 3] = 255;
                Healer hf = new Healer(hw2, hh2, 1f);
                bool passthru = ReferenceEquals(hf.Feed(lit), lit);
                byte[] got = hf.Feed(blk);
                bool swapped = !ReferenceEquals(got, blk);
                long litR = 0, gotR = 0;
                for (int i = 0; i < hw2 * hh2; i++) { litR += lit[i * 4 + 2]; gotR += got[i * 4 + 2]; }
                Healer hz = new Healer(hw2, hh2, 0f);
                hz.Feed(lit);
                bool inert = ReferenceEquals(hz.Feed(blk), blk);
                bool healOk = passthru && swapped && inert && gotR > litR * 95 / 100;
                Console.WriteLine((healOk ? "PASS" : "FAIL") + "  heal holds the lit frame across a gap (" +
                                  (gotR * 100 / litR) + "% of it), strength 0 leaves the gap");
                if (!healOk) failures++;
            }

            // 3. decode path works
            try
            {
                string asset = EnsureAsset(opt.Verbose);
                SmokeSource src = SmokeSource.Open(asset, 640, 360);
                byte[] f = src.Next();
                bool got = f != null && f.Length >= src.Width * src.Height * 4;
                Console.WriteLine((got ? "PASS" : "FAIL") + "  decode " + src.Width + "x" + src.Height +
                                  " bytes=" + (f == null ? 0 : f.Length) +
                                  " empties=" + src.LastEmptySamples + " ts=" + src.LastTimestamp);
                if (!got && src.LastError.Length > 0) Console.WriteLine("      " + src.LastError);
                if (!got) failures++;
                src.Dispose();
            }
            catch (Exception ex)
            {
                Console.WriteLine("FAIL  decode: " + ex.Message);
                failures++;
            }

            Console.WriteLine(failures == 0 ? "RESULT: PASS" : "RESULT: FAIL (" + failures + ")");
            return failures == 0 ? 0 : 1;
        }

        private static void ListPalettes()
        {
            Console.WriteLine("palettes (use --palette <name>):");
            string[] names = new string[Grade.Presets.Count];
            Grade.Presets.Keys.CopyTo(names, 0);
            Array.Sort(names);
            for (int i = 0; i < names.Length; i++)
                Console.WriteLine("  " + names[i].PadRight(10) + "  " + Grade.Presets[names[i]]);
            Console.WriteLine();
            Console.WriteLine();
            Console.WriteLine("hue/sat/gain apply the SAME shift to the whole frame, so the footage's two");
            Console.WriteLine("inks each land on their own new hue (ember => one cool + one warm ink).");
            Console.WriteLine("ramp= collapses everything onto one gradient - that is the single-colour look.");
            Console.WriteLine("duo=  gives each of the two dyes its own colour, so both stay distinct.");
            Console.WriteLine();
            Console.WriteLine("or grade inline:  --palette \"hue=120,sat=1.8,gain=0.7,1.4,1.2\"");
            Console.WriteLine("single-colour:    --palette \"ramp=#000000,#1b3a2f,#8affc1,#ffffff\"");
            Console.WriteLine("two-ink:          --palette \"duo=#ff6b00,#00e5ff\"");
            Console.WriteLine("ramp over time:   --palette ember --progress deepsea --progress-minutes 10");
        }

        private static void Help()
        {
            Console.WriteLine("LumenRefresh - ASUS Lumina OLED pixel-refresh clone");
            Console.WriteLine();
            Console.WriteLine("  LumenRefresh.exe [options]");
            Console.WriteLine();
            Console.WriteLine("COLOUR");
            Console.WriteLine("  --palette <name|spec>  colour grade (see --list-palettes)");
            Console.WriteLine("  --grade <spec>         extra grade layered on top");
            Console.WriteLine("  --duo <#a,#b>          two-ink duotone: each dye gets its own colour");
            Console.WriteLine("  --luma <0..1>          normalise the grade to this mean luminance, so every");
            Console.WriteLine("                         palette delivers a comparable refresh dose");
            Console.WriteLine("  --progress <name>      ramp from --palette toward this one over the session");
            Console.WriteLine("  --progress-minutes <f> ramp length, default 10");
            Console.WriteLine("  --palette \"a+b\"         crossfade a into b and back once per loop, so the seam");
            Console.WriteLine("                         is invisible at both ends");
            Console.WriteLine("  --blend-period <n>     loops per a+b sweep, default 1");
            Console.WriteLine("  --gamma <f>            multiply the grade's gamma (1.0 = untouched)");
            Console.WriteLine();
            Console.WriteLine("PATTERN");
            Console.WriteLine("  --speed <f>            playback speed, default 1.0");
            Console.WriteLine("  --render <WxH>         decode size, default 1920x1080 (window always");
            Console.WriteLine("                         grades at panel size and cover-crops)");
            Console.WriteLine("  --zoom <f>             zoom into the footage");
            Console.WriteLine("  --mirror               flip horizontally every other loop");
            Console.WriteLine("  --kaleido              mirror-tile the frame");
            Console.WriteLine("  --orbit                move the crop window each loop, so the bright passages");
            Console.WriteLine("                         do not keep landing on the same pixels");
            Console.WriteLine("  --dwell                pick each loop's crop by lowest luminance-seconds so far");
            Console.WriteLine("  --quadrant <0..3>      start the orbit at this position instead of 0");
            Console.WriteLine("  --pulse <f>            brightness breathing, 0..1");
            Console.WriteLine("  --shift <n>            OLED pixel-shift amplitude (0 disables)");
            Console.WriteLine("  --shift-px             shift raw pixels instead of whole RGB triads");
            Console.WriteLine("  --no-shift             disable pixel shift");
            Console.WriteLine("  --ripple <px>          travelling wave through the sample grid");
            Console.WriteLine("  --scan <0..1>          soft scanline darkening");
            Console.WriteLine("  --bloom <0..1>         glow around the bright passages, blurred at 1/16 and");
            Console.WriteLine("                         added back; free in --export, live it is the frame");
            Console.WriteLine("                         budget, so lower --render to 1920x1080 if it drops");
            Console.WriteLine("  --grain <0..1>         static film grain, scrolled per frame");
            Console.WriteLine("  --heal [s]             dissolve the source's black gaps into the last lit");
            Console.WriteLine("                         frame instead of cutting to black");
            Console.WriteLine();
            Console.WriteLine("RUN CONTROL");
            Console.WriteLine("  --minutes <f>          auto-exit after N minutes");
            Console.WriteLine("  --seconds <n>          loop length in seconds");
            Console.WriteLine("  --source <file>        play a different clip instead of the embedded one");
            Console.WriteLine("  --hud                  reserved");
            Console.WriteLine("  --watch                start a refresh whenever the machine is idle");
            Console.WriteLine("  --idle <n>             idle seconds before --watch fires, default 120");
            Console.WriteLine();
            Console.WriteLine("OUTPUT");
            Console.WriteLine("  --export <file.mp4>    render instead of playing (needs ffmpeg on PATH,");
            Console.WriteLine("                         or --ffmpeg <path>)");
            Console.WriteLine("  --export-size <WxH>    export resolution, default 1920x1080");
            Console.WriteLine("  --export-seconds <f>   export length, default is the full loop");
            Console.WriteLine("  --export-all <dir>     one clip per palette, named <dir>/<palette>.mp4");
            Console.WriteLine("  --palettes <a,b,c>     the subset --export-all renders, default every one");
            Console.WriteLine();
            Console.WriteLine("SHELL");
            Console.WriteLine("  --install-scr [--scr-timeout n]   register as the current user's screen");
            Console.WriteLine("                                    saver (HKCU only, -1 = never)");
            Console.WriteLine("  --uninstall-scr                   undo that");
            Console.WriteLine("  --list-palettes        show the built-in grades");
            Console.WriteLine("  --dump <dir> [--times a,b,c]   write graded stills instead of playing");
            Console.WriteLine("  --selftest             verify grading and decode");
            Console.WriteLine();
            Console.WriteLine("Exit: any key or mouse click, or a 12px mouse move.");
        }
    }
}
