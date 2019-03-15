Description
===========

xaa is a many-in-one antialiasing function for VapourSynth.

This is a port of the Avisynth function of the same name, version
1.2.1.


Usage
=====
::

    xaa(clip[, ow=clip.width, oh=clip.height, ss, ssw=ss, ssh=ss, mode="sr SangNom", uscl="Spline36", dscl="Spline36", csharp=0, cstr=-1.0, mask=1, mtype="TEdgeMask", mthr=8.0, chroma=0, cplace="MPEG2", nns=1, eedimthr=0.0, eediA=0.2, eediB=0.25, eediG=20.0])

Parameters:
    *clip*
        A clip to process. It must have constant format and
        dimensions, 8..16 bit integer sample type, and it must be
        GRAY, YUV420, YUV422, or YUV444.

    *ow*, *oh*
        The output width and height.

        Useful for when the video is going to be resized after
        antialising.

        Use a negative value for either to disable resizing after
        supersampling.

        Default: clip.width, clip.height.

    *ss*
        The multiplier for determining the supersampled resolution
        which is then rounded to mod4.

        Default: 1.0 (no supersampling) for double rate ("dr") and
        double image ("di") antialiasing modes (see the *mode*
        parameter). Otherwise, 2.0.

    *ssw*, *ssh*
        Allows separate control of the supersampled width and height.
        Overrides the *ss* parameter.
        
        When specified as a float, they act as a multiplier like the
        *ss* parameter. When specified as an int, the given value is
        used for the supersampled width or height without rounding to
        mod4.

        Default: *ss*.

    *mode*
        Specifies how to perform antialiasing in the format
        "[aa mode][direction][passes] [type] [sclip]" with the
        settings below available for each option. Antialiasing can
        also be disabled with "null".

        AA Mode
            The antialiasing mode determines what method of
            antialiasing is used.
            
            "sr" uses single rate deinterlacing, discarding one field
            of the frame and interpolating it from the remaining
            field.
            
            "dr" uses double rate deinterlacing, interpolating
            full-height frames from both fields and then blending the
            two together.
            
            "di" doubles the image height by interpolating every other
            line for the first pass, uses single rate deinterlacing
            for subsequent passes, and then downscales back to the
            original resolution.
            
        Direction
            By setting the direction to "h" or "v", antialiasing can
            be applied only horizontally or vertically. If the
            direction is set to "b" or omitted, antialiasing will be
            applied in both directions.

        Passes
            The more passes used, the stronger the antialiasing will
            be. If the number of passes is omitted, it will default to
            1.
            
            Possible values: 1 to 9.

        Type
            The type determines which deinterlacing plugin is used for
            antialiasing.
            
            Possible values: SangNom, znedi3, nnedi3cl, eedi3, eedi2.

        Sclip
            The sclip option only applies when the aa type is set to
            eedi3 and will be undefined if omitted.
            
            If specified, the given deinterlacer or resize kernel will
            be used to generate the sclip for eedi3.
            
            See eedi3's documentation for more details.
            
            Possible values: SangNom, znedi3, nnedi3cl, eedi2,
            Bilinear, Bicubic, Point, Lanczos, Spline16, Spline36.

        Preset modes which change the default settings to mimic other
        antialiasing functions are also available: "maa2", "daa",
        "Mrdaa" or "MrdaaLame", "santiag".

        Equivalent settings:
            maa2:    ``xaa(mtype="Sobel", mthr=7)``
            
            daa:     ``xaa(mode="drv znedi3", csharp=1, mask=0, chroma=1)``
            
            Mrdaa:   ``xaa(mode="null", uscl="znedi3", csharp=2, cstr=1.0, mask=0, chroma=1)``
            
            santiag: ``xaa(mode="di2 znedi3", mask=0, chroma=1)``

        Default: "sr SangNom".

    *uscl*, *dscl*
        The resize kernels used when upscaling, such as when
        supersampling, and when downscaling, such as when scaling back
        to the input resolution after supersampling. Supports all of
        VapourSynth's internal resizers, and for upscaling, "znedi3",
        "nnedi3cl", "eedi3", and "eedi2" can also be used for their
        rpow2 image enlargement.

        For eedi3 upscaling, the sclip setting can be specified with
        a resize kernel name or edi method on the end of the string.
        E.g. "eedi3 znedi3" to upscale with eedi3 using znedi3 as the
        sclip.

        Default: "Spline36", except when *mode* is "Mrdaa" or
        "MrdaaLame" *uscl* defaults to "znedi3".

    *csharp*
        0: No contra-sharpening.
        
        1: Applies contra-sharpening before scaling to output
        resolution.
        
        2: Applies contra-sharpening after scaling to output
        resolution.

        Default: 0, except when *mode* is "daa" *csharp* defaults to
        1, and when *mode* is "Mrdaa" or "MrdaaLame" *csharp* defaults
        to 2.

    *cstr*
        Controls the strength of the contra-sharpening.
        
        Any negative value uses RemoveGrain(mode=11) as in daa.
        A positive value uses Blur as in Mrdaa up to a max of 7.9.
        A value of 0 disables contra-sharpening and overrides the
        *csharp* parameter.

        Default: -1.0, except when *mode* is "Mrdaa" or "MrdaaLame"
        *cstr* defaults to 1.0.

    *mask*
        0: Processes the entire frame
        
        1: Processes edges only
        
        2: Processes everything except edges

        A negative value will show an overlay of the mask.
        
        Default: 1, except when *mode* is "daa", "Mrdaa", "MrdaaLame",
        or "santiag" *mask* defaults to 0.

    *mtype*
        The type of edge mask to use. Options are "TEdgeMask",
        "TCanny", "Prewitt", and "Sobel".

        TEdgeMask's type parameter can be set with a number on the end
        of the string. E.g. "TEdgeMask5" for type=5. If no number is
        given, the default of 4 is used.

        This setting also determines the mask type for the *eedimthr*
        parameter.

        Default: "TEdgeMask", except when *mode* is "maa2" *mtype*
        defaults to "Sobel".

    *mthr*
        The threshold of the edge mask. Rounded to the nearest integer
        when *mtype* is "Sobel" or "Prewitt".
        
        When *mask* is 1, lower values result in more edges getting
        antialiased.
        
        When *mask* is 2, lower values result in fewer edges getting
        excluded.

        Default: 8.0, except when *mode* is "maa2" *mthr* defaults to
        7.0.

    *chroma*
        0: Processes the luma plane only
        
        1: Processes both the luma and chroma planes
        
        2: Processes the chroma planes only

        Default: 0, except when *mode* is "daa", "Mrdaa", "MrdaaLame",
        or "santiag" *chroma* defaults to 1.
        
    *cplace*
        Specifies the input's chroma placement. Options are "MPEG1"
        and "MPEG2".
        
        Only applies to formats with subsampled chroma. Note that only
        formats with 4:2:0 subsampling should be able to have MPEG1
        chroma placement.
    
        Default: "MPEG2".
        
    *nns*
        znedi3's nns parameter for znedi3 and nnedi3cl antialiasing.
        Ranges from 0 to 4.
        
        Higher values will provide better quality but will be slower.
        This setting doesn't affect upscaling with znedi3 or nnedi3cl.
    
        Default: 1.
        
    *eedimthr*
        A value greater than 0 creates an edge mask with the given
        value's threshold to be used with eedi3 antialiasing and
        upscaling. Edge-directed interpolation will be used only on
        masked edges, increasing eedi3's speed as the threshold is
        raised, but at the risk of excluding edges that need
        antialiasing.
    
        Default: 0.0.
        
    *eediA*, *eediB*, *eediG*
        eedi3's *alpha*, *beta*, and *gamma* parameters for eedi3
        antialiasing and upscaling.

        They adjust the balance between connecting lines and creating
        artifacts. *eediA* and *eediB* must be in the range 0 to 1 and
        their sum can't exceed 1.
        
        See eedi3's documentation for more info.
    
        Default: 0.2, 0.25, and 20.0.
        

Requirements
============

   * `EEDI2 <https://github.com/HomeOfVapourSynthEvolution/VapourSynth-EEDI2/releases>`_
   * `EEDI3 <https://github.com/HomeOfVapourSynthEvolution/VapourSynth-EEDI3/releases>`_
   * `ZNEDI3 <https://github.com/sekrit-twc/znedi3/releases>`_
   * `NNEDI3CL <https://github.com/HomeOfVapourSynthEvolution/VapourSynth-NNEDI3CL/releases>`_
   * `RGVS (included with VapourSynth) <http://www.vapoursynth.com/doc/plugins/rgvs.html>`_
   * `SangNom <https://github.com/dubhater/vapoursynth-sangnom/releases>`_
   * `TCanny <https://github.com/HomeOfVapourSynthEvolution/VapourSynth-TCanny/releases>`_
   * `TEdgeMask <https://github.com/dubhater/vapoursynth-tedgemask/releases>`_


License
=======

???
