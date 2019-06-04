import vapoursynth as vs


def is420(clip):
    return clip.format.color_family == vs.YUV and clip.format.subsampling_w == 1 and clip.format.subsampling_h == 1

def is422(clip):
    return clip.format.color_family == vs.YUV and clip.format.subsampling_w == 1 and clip.format.subsampling_h == 0

def is444(clip):
    return clip.format.color_family == vs.YUV and clip.format.subsampling_w == 0 and clip.format.subsampling_h == 0

def isGray(clip):
    return clip.format.color_family == vs.GRAY


def Blur(clip, amount=0, planes=None):
    lower_limit = 0
    upper_limit = 1.5849625
    if amount < lower_limit or amount > upper_limit:
        raise ValueError("Blur: 'amount' must be between {} and {}.".format(lower_limit, upper_limit))

    center_weight = 1 / pow(2, amount)
    side_weight = (1 - center_weight) / 2

    corner = int(side_weight * side_weight * 1000 + 0.5)
    side = int(side_weight * center_weight * 1000 + 0.5)
    center = int(center_weight * center_weight * 1000 + 0.5)

    blur_matrix = [corner,   side, corner,
                     side, center,   side,
                   corner,   side, corner]

    return clip.std.Convolution(matrix=blur_matrix, planes=planes)


# Recursive helper functions for repeated edi image doubling
# When calling these functions, the f and t parameters should always be left at their default values.
# They're used only to control behavior during recursion and changing them will cause a malfunction.

def edi_rpow2_znedi3(clip, rfactorX, rfactorY, alignc=False, nsize=None, nns=None, qual=None, etype=None, pscrn=None, opt=None, int16_prescreener=None, int16_predictor=None, exp=None, f=True, turned=False):
    core = vs.get_core()

    # If alignc=true, always use field=1 for doubling the width
    # to maintain alignment of horizontally subsampled chroma.
    field2 = int(f)
    
    if alignc:
        field1 = 1
    else:
        field1 = field2
    
    # Only turn right if doubling the width and the input isn't already turned
    dbl = clip
    if not turned and rfactorX > 1:
        dbl = dbl.std.Transpose()
        turned = True
        
    if rfactorX > 1:
        dbl = dbl.znedi3.nnedi3(field=field1, dh=True, nsize=nsize, nns=nns, qual=qual, etype=etype, pscrn=pscrn, opt=opt, int16_prescreener=int16_prescreener, int16_predictor=int16_predictor, exp=exp)
        
    # Only turn left if the height is going to be doubled or after the last iteration of doubling the width.
    # This avoids unnecessary turning when only the width is doubled repeatedly.
    if turned and (rfactorY > 1 or rfactorX == 2):
        dbl = dbl.std.Transpose()
        turned = False
        
    if rfactorY > 1:
        dbl = dbl.znedi3.nnedi3(field=field2, dh=True, nsize=nsize, nns=nns, qual=qual, etype=etype, pscrn=pscrn, opt=opt, int16_prescreener=int16_prescreener, int16_predictor=int16_predictor, exp=exp)
    
    if rfactorX > 1 or rfactorY > 1:
        return edi_rpow2_znedi3(clip=dbl, rfactorX=max(1, rfactorX // 2), rfactorY=max(1, rfactorY // 2), alignc=alignc, nsize=nsize, nns=nns, qual=qual, etype=etype, pscrn=pscrn, opt=opt, int16_prescreener=int16_prescreener, int16_predictor=int16_predictor, exp=exp, f=False, turned=turned)
    else:
        return clip
    

def edi_rpow2_nnedi3cl(clip, rfactorX, rfactorY, alignc=False, nsize=None, nns=None, qual=None, etype=None, pscrn=None, f=True, turned=False):
    core = vs.get_core()

    # FIXME Not using the dw parameter because it behaves differently from the Avisynth version.
    
    # If alignc=true, always use field=1 for doubling the width
    # to maintain alignment of horizontally subsampled chroma.
    field2 = int(f)
    
    if alignc:
        field1 = 1
    else:
        field1 = field2
    
    # Only turn right if doubling the width and the input isn't already turned
    dbl = clip
    if not turned and rfactorX > 1:
        dbl = dbl.std.Transpose()
        turned = True
        
    if rfactorX > 1:
        dbl = dbl.nnedi3cl.NNEDI3CL(field=field1, dh=True, nsize=nsize, nns=nns, qual=qual, etype=etype, pscrn=pscrn)
        
    # Only turn left if the height is going to be doubled or after the last iteration of doubling the width.
    # This avoids unnecessary turning when only the width is doubled repeatedly.
    if turned and (rfactorY > 1 or rfactorX == 2):
        dbl = dbl.std.Transpose()
        turned = False
        
    if rfactorY > 1:
        dbl = dbl.nnedi3cl.NNEDI3CL(field=field2, dh=True, nsize=nsize, nns=nns, qual=qual, etype=etype, pscrn=pscrn)
    
    if rfactorX > 1 or rfactorY > 1:
        return edi_rpow2_nnedi3cl(clip=dbl, rfactorX=max(1, rfactorX // 2), rfactorY=max(1, rfactorY // 2), alignc=alignc, nsize=nsize, nns=nns, qual=qual, etype=etype, pscrn=pscrn, f=False, turned=turned)
    else:
        return clip


def edi_rpow2_eedi2(clip, rfactorX, rfactorY, alignc=False, mthresh=None, lthresh=None, vthresh=None, estr=None, dstr=None, maxd=None, map=None, nt=None, pp=None, f=True, turned=False):
    core = vs.get_core()

    field2 = int(f)
    
    if alignc:
        field1 = 1
    else:
        field1 = field2
        
    dbl = clip
    if not turned and rfactorX > 1:
        dbl = dbl.std.Transpose()
        turned = True
    
    if rfactorX > 1:
        dbl = dbl.eedi2.EEDI2(field=field1, mthresh=mthresh, lthresh=lthresh, vthresh=vthresh, estr=estr, dstr=dstr, maxd=maxd, map=map, nt=nt, pp=pp)
        
    if turned and (rfactorY > 1 or rfactorX == 2):
        dbl = dbl.std.Transpose()
        turned = False
        
    if rfactorY > 1:
        dbl = dbl.eedi2.EEDI2(field=field2, mthresh=mthresh, lthresh=lthresh, vthresh=vthresh, estr=estr, dstr=dstr, maxd=maxd, map=map, nt=nt, pp=pp)
        
    if rfactorX > 1 or rfactorY > 1:
        return edi_rpow2_eedi2(clip=dbl, rfactorX=max(1, rfactorX // 2), rfactorY=max(1, rfactorY // 2), alignc=alignc, mthresh=mthresh, lthresh=lthresh, vthresh=vthresh, estr=estr, dstr=dstr, maxd=maxd, map=map, nt=nt, pp=pp, f=False, turned=turned)
    else:
        return clip
    
    
def edi_rpow2_eedi3(clip, rfactorX, rfactorY, alignc=False, alpha=None, beta=None, gamma=None, nrad=None, mdis=None, hp=None, ucubic=None, cost3=None, vcheck=None, vthresh0=None, vthresh1=None, vthresh2=None, sclip=None, sclip_params=dict(), mclip=None, opt=None, f=True, turned=False, nnrep=False):
    core = vs.get_core()

    field2 = int(f)
    
    if alignc:
        field1 = 1
    else:
        field1 = field2
        
    # Use a src_left or src_top shift dependent on the field when resizing
    # for the sclip or mclip to keep it in alignment with the eedi3 clip.
    # Additionally, the vertical shift for YV12 chroma is doubled,
    # so the chroma must be resized separately when doubling the height.
    if field1 == 1:
        rshift1 = 0.25
    else:
        rshift1 = -0.25
        
    if field2 == 1:
        rshift2 = 0.25
    else:
        rshift2 = -0.25
        
    dbl = clip
    if not turned and rfactorX > 1:
        dbl = dbl.std.Transpose()
        turned = True

    
    if rfactorX > 1:
        if sclip == "":
            sclip2 = None
        elif sclip == "znedi3":
            sclip2 = dbl.znedi3.nnedi3(field=field1, dh=True, **sclip_params)
        elif sclip == "nnedi3cl":
            sclip2 = dbl.nnedi3cl.NNEDI3CL(field=field1, dh=True, **sclip_params)
        elif sclip == "eedi2":
            sclip2 = dbl.eedi2.EEDI2(field=field1, **sclip_params)
        else:
            sclip2 = eval("core.resize." + sclip)(clip=dbl, width=dbl.width, height=dbl.height * 2, src_left=0, src_top=rshift1, **sclip_params)
            
        mclip1 = mclip
        if mclip1 is not None:
            mclip1 = mclip1.std.Transpose()
        
        dbl = dbl.eedi3m.EEDI3(field=field1, dh=True, alpha=alpha, beta=beta, gamma=gamma, nrad=nrad, mdis=mdis, hp=hp, ucubic=ucubic, cost3=cost3, vcheck=vcheck, vthresh0=vthresh0, vthresh1=vthresh1, vthresh2=vthresh2, sclip=sclip2, mclip=mclip1, opt=opt)
        
        if nnrep and sclip == "znedi3":
            dbl = core.rgvs.Repair(clip=dbl, repairclip=sclip2, mode=9)
    
        if mclip is not None:
            mclip = core.resize.Spline36(clip=mclip, width=mclip.width * 2, height=mclip.height, src_left=rshift1, src_top=0)
            mclip = core.std.Binarize(clip=mclip)
            
            
    if turned and (rfactorY > 1 or rfactorX == 2):
        dbl = dbl.std.Transpose()
        turned = False
        
    if rfactorY > 1:
        if sclip == "":
            sclip2 = None
        elif sclip == "znedi3":
            sclip2 = dbl.znedi3.nnedi3(field=field2, dh=True, **sclip_params)
        elif sclip == "nnedi3cl":
            sclip2 = dbl.nnedi3cl.NNEDI3CL(field=field2, dh=True, **sclip_params)
        elif sclip == "eedi2":
            sclip2 = dbl.eedi2.EEDI2(field=field2, **sclip_params)
        else:
            sclip2 = eval("core.resize." + sclip)(clip=dbl, width=dbl.width, height=dbl.height * 2, src_left=0, src_top=rshift2, **sclip_params)
            
        dbl = dbl.eedi3m.EEDI3(field=field2, dh=True, alpha=alpha, beta=beta, gamma=gamma, nrad=nrad, mdis=mdis, hp=hp, ucubic=ucubic, cost3=cost3, vcheck=vcheck, vthresh0=vthresh0, vthresh1=vthresh1, vthresh2=vthresh2, sclip=sclip2, mclip=mclip, opt=opt)
        
        if nnrep and sclip == "znedi3":
            dbl = core.rgvs.Repair(clip=dbl, repairclip=sclip2, mode=9)
            
        if mclip is not None:
            mclip = core.resize.Spline36(clip=mclip, width=mclip.width, height=mclip.height * 2, src_left=0, src_top=rshift2)
            mclip = core.std.Binarize(clip=mclip)
            
    if rfactorX > 1 or rfactorY > 1:
        return edi_rpow2_eedi3(clip=dbl, rfactorX=max(1, rfactorX // 2), rfactorY=max(1, rfactorY // 2), alignc=alignc, alpha=alpha, beta=beta, gamma=gamma, nrad=nrad, mdis=mdis, hp=hp, ucubic=ucubic, cost3=cost3, vcheck=vcheck, vthresh0=vthresh0, vthresh1=vthresh1, vthresh2=vthresh2, sclip=sclip, sclip_params=sclip_params, mclip=mclip, opt=opt, f=False, turned=turned, nnrep=nnrep)
    else:
        return clip




def edi_rpow2(clip, rfactorX=2, rfactorY=None, edi="znedi3", cshift="", fwidth=None, fheight=None,
              cplace="MPEG2", planes=None, bordfix=None, YV12cfix=True,
              nsize=0, nns=3, qual=None, etype=None, pscrn=None, opt=None, int16_prescreener=None, int16_predictor=None, exp=None,
              alpha=None, beta=None, gamma=None, nrad=None, mdis=None, hp=None, ucubic=None, cost3=None,
              vcheck=None, vthresh0=None, vthresh1=None, vthresh2=None, sclip="", sclip_params=dict(), mclip=None,
              mthresh=None, lthresh=None, vthresh=None, estr=None, dstr=None, maxd=None, map=None, nt=None, pp=None, nnrep=False):
    core = vs.get_core()

    
    def Default(param, value):
        if param is None:
            return value
        else:
            return param
    
    if clip.width == 0 or clip.height == 0:
        raise ValueError("edi_rpow2: 'clip' must have constant dimensions.")
    
    if clip.format is None:
        raise ValueError("edi_rpow2: 'clip' must have constant format.")

    iw = clip.width
    ih = clip.height
    
    rfactorY = Default(rfactorY, rfactorX)
    fwidth = Default(fwidth, iw * rfactorX)
    fheight = Default(fheight, ih * rfactorY)
    planes = Default(planes, list(range(clip.format.num_planes)))
    bordfix = Default(bordfix, edi != "eedi3")
    
    if rfactorX <= 0 or (rfactorX & (rfactorX - 1) != 0):
        raise ValueError("edi_rpow2: 'rfactorX' must be a power of 2.")
    
    if rfactorY <= 0 or (rfactorY & (rfactorY - 1) != 0):
        raise ValueError("edi_rpow2: 'rfactorY' must be a power of 2.")
    
    acceptable_edi = ["znedi3", "nnedi3cl", "eedi3", "eedi2"]
    if edi not in acceptable_edi:
        raise ValueError("edi_rpow2: 'edi' must be one of {}.".format(acceptable_edi))
    
    acceptable_cshift = ["", "Bilinear", "Bicubic", "Point", "Lanczos", "Spline16", "Spline36"]
    if cshift not in acceptable_cshift:
        raise ValueError("edi_rpow2: 'cshift' must be one of {}.".format(acceptable_cshift))
    
    acceptable_cplace = ["MPEG1", "MPEG2"]
    if cplace not in acceptable_cplace:
        raise ValueError("edi_rpow2: 'cplace' must be one of {}.".format(acceptable_cplace))
    
    acceptable_sclip = acceptable_cshift + ["znedi3", "nnedi3cl", "eedi2"]
    if sclip not in acceptable_sclip:
        raise ValueError("edi_rpow2: 'sclip' must be one of {}.".format(acceptable_sclip))
    
    if not isinstance(sclip_params, dict):
        raise ValueError("edi_rpow2: 'sclip_params' must be a dict.")
    
    # Override the fwidth and fheight parameters if not correcting the center shift
    if cshift == "":
        fwidth = iw * rfactorX
        fheight = ih * rfactorY
        
    csp = clip.format.id
    
    hssc12 = clip.format.subsampling_w
    vssc12 = clip.format.subsampling_h
    
    alignc = hssc12
    
    if hssc12 and fwidth % 2:
        raise ValueError("edi_rpow2: 'fwidth' of {} must be a multiple of 2.".format(clip.format.name))
    
    if vssc12 and fheight % 2:
        raise ValueError("edi_rpow2: 'fheight' of {} must be a multiple of 2.".format(clip.format.name))
    
    # Input and output chroma width and height determined by subsampling
    iw_c = iw >> hssc12
    ih_c = ih >> vssc12
    
    fwidth_c = fwidth >> hssc12
    fheight_c = fheight >> vssc12
    
    # Center shift correction values
    if rfactorX == 1:
        cshiftH = 0
    elif hssc12:
        cshiftH = -0.5 * (rfactorX - 1)
    else:
        cshiftH = -0.5
        
    if rfactorY == 1:
        cshiftV = 0
    else:
        cshiftV = -0.5
        
    if hssc12:
        cshiftH_c = cshiftH / 2.0
    else:
        cshiftH_c = cshiftH
        
    if vssc12 and rfactorY > 1:
        cshiftV_c = cshiftV / 2.0 - 0.25
    else:
        cshiftV_c = cshiftV
        
    # Add the MPEG1 or MPEG2 chroma shift correction to the cshiftH_c value
    if hssc12:
        MPEG1shift = -0.25 * (rfactorX - 1)
        MPEG2shift = 0.25 * (1.0 - iw * rfactorX / fwidth)
        
        if cplace == "MPEG1":
            cshiftH_c = cshiftH_c + MPEG1shift
        elif cplace == "MPEG2" and cshift != "Point":
            cshiftH_c = cshiftH_c + MPEG2shift
    
    # Pad at least four rows if bordfix=true.
    if bordfix and rfactorX > 1:
        padR = padL = 4
    else:
        padR = padL = 0
        
    if bordfix and rfactorY > 1:
        padT = padB = 4
    else:
        padT = padB = 0
        
    padL_c = padL >> hssc12
    padR_c = padR >> hssc12
    padT_c = padT >> vssc12
    padB_c = padB >> vssc12
    
    einput = clip
    emclip = mclip
    if bordfix:
        einput = core.resize.Point(clip=einput,
                                   width=iw + padL + padR,
                                   height=ih + padT + padB,
                                   src_left=-padL,
                                   src_top=-padT,
                                   src_width=iw + padL + padR,
                                   src_height=ih + padT + padB)
        if emclip is not None:
            emclip = core.resize.Point(clip=emclip,
                                       width=iw + padL + padR,
                                       height=ih + padT + padB,
                                       src_left=-padL,
                                       src_top=-padT,
                                       src_width=iw + padL + padR,
                                       src_height=ih + padT + padB)
    
    padL = [padL, padL_c, padL_c]
    padR = [padR, padR_c, padR_c]
    padT = [padT, padT_c, padT_c]
    padB = [padB, padB_c, padB_c]
    
    fwidth = [fwidth, fwidth_c, fwidth_c]
    fheight = [fheight, fheight_c, fheight_c]
    
    cshiftH = [cshiftH, cshiftH_c, cshiftH_c]
    cshiftV = [cshiftV, cshiftV_c, cshiftV_c]
    
    pow2 = []
    
    blank = core.std.BlankClip(clip=clip, width=fwidth[0], height=fheight[0])
    
    for plane in range(einput.format.num_planes):
        if not plane in planes:
            pow2.append(core.std.ShufflePlanes(clips=blank, planes=plane, colorfamily=vs.GRAY))
            
            continue
        
        p = core.std.ShufflePlanes(clips=einput, planes=plane, colorfamily=vs.GRAY)
        
        # Image enlargement
        if edi == "znedi3":
            p = edi_rpow2_znedi3(clip=p, rfactorX=rfactorX, rfactorY=rfactorY, alignc=alignc, nsize=nsize, nns=nns, qual=qual, etype=etype, pscrn=pscrn, opt=opt, int16_prescreener=int16_prescreener, int16_predictor=int16_predictor, exp=exp)
        elif edi == "nnedi3cl":
            p = edi_rpow2_nnedi3cl(clip=p, rfactorX=rfactorX, rfactorY=rfactorY, alignc=alignc, nsize=nsize, nns=nns, qual=qual, etype=etype, pscrn=pscrn)
        elif edi == "eedi3":
            emclip_p = emclip
            if emclip_p is not None:
                emclip_p = core.std.ShufflePlanes(clips=emclip_p, planes=plane, colorfamily=vs.GRAY)
            
            p = edi_rpow2_eedi3(clip=p, rfactorX=rfactorX, rfactorY=rfactorY, alignc=alignc, alpha=alpha, beta=beta, gamma=gamma, nrad=nrad, mdis=mdis, hp=hp, ucubic=ucubic, cost3=cost3, vcheck=vcheck, vthresh0=vthresh0, vthresh1=vthresh1, vthresh2=vthresh2, sclip=sclip, sclip_params=sclip_params, mclip=emclip_p, opt=opt, nnrep=nnrep)
        elif edi == "eedi2":
            p = edi_rpow2_eedi2(clip=p, rfactorX=rfactorX, rfactorY=rfactorY, alignc=alignc, mthresh=mthresh, lthresh=lthresh, vthresh=vthresh, estr=estr, dstr=dstr, maxd=maxd, map=map, nt=nt, pp=pp)
            
        # Crop off the padding
        p = core.std.Crop(clip=p,
                          left=padL[plane] * rfactorX,
                          top=padT[plane] * rfactorY,
                          right=padR[plane] * rfactorX,
                          bottom=padB[plane] * rfactorY)
        
        # Center shift correction
        if cshift != "":
            p = eval("core.resize." + cshift)(clip=p,
                                              width=fwidth[plane],
                                              height=fheight[plane],
                                              src_left=cshiftH[plane],
                                              src_top=cshiftV[plane])
        
        pow2.append(p)
        
    # Even if the center shift isn't corrected,
    # doubling the height of YV12 causes a vertical chroma shift that needs to be corrected
    if cshift == "" and is420(clip) and YV12cfix and rfactorY > 1:
        for plane in range(1, einput.format.num_planes):
            if plane in planes:
                pow2[plane] = core.resize.Spline36(clip=pow2[plane],
                                                   width=fwidth[plane],
                                                   height=fheight[plane],
                                                   src_left=0,
                                                   src_top=-0.25)
    
    if len(pow2) == 1:
        return pow2[0]
    else:
        return core.std.ShufflePlanes(clips=pow2, planes=[0, 0, 0], colorfamily=clip.format.color_family)


def xaa(clip, ow=None, oh=None, ss=None, ssw=None, ssh=None, mode="sr SangNom", uscl=None, dscl="Spline36", csharp=None, cstr=None, mask=None, mtype=None, mthr=None, chroma=None, cplace="MPEG2", nns=1, eedimthr=0.0, eediA=0.2, eediB=0.25, eediG=20.0):
    core = vs.get_core()
    
    
    
    def Default(param, value):
        if param is None:
            return value
        else:
            return param
    
    
    # Avisynth's Round function doesn't do quite the same thing as Python's round function.
    def AvisynthRound(value):
        if value < 0:
            return -int(-value + 0.5)
        else:
            return int(value + 0.5)
    
    
    # Resize the luma and the chroma separately in order to use different subpixel shifts.
    def ResizeSeparately(clip, width, height, src_left, src_top, kernel="Spline36", cplace="MPEG2"):
        core = vs.get_core()

        if not isinstance(clip, vs.VideoNode):
            raise ValueError("ResizeSeparately: 'clip' must be a clip.")
        
        if clip.format is None:
            raise ValueError("ResizeSeparately: 'clip' must have constant format.")
        
        if clip.width == 0 or clip.height == 0:
            raise ValueError("ResizeSeparately: 'clip' must have constant dimensions.")
        
        ratio = 1 << clip.format.subsampling_w
        if width % ratio != 0:
            raise ValueError("ResizeSeparately: 'width' must be a multiple of {}. Instead it is {}.".format(ratio, width))
        
        ratio = 1 << clip.format.subsampling_h
        if height % ratio != 0:
            raise ValueError("ResizeSeparately: 'height' must be a multiple of {}. Instead it is {}.".format(ratio, height))
        
        if not isinstance(src_left, list) or len(src_left) != 2:
            raise ValueError("ResizeSeparately: 'src_left' must be a list of two numbers.")
        
        if not isinstance(src_top, list) or len(src_top) != 2:
            raise ValueError("ResizeSeparately: 'src_top' must be a list of two numbers.")
        
        if src_left[0] == src_left[1] and src_top[0] == src_top[1]:
            raise ValueError("ResizeSeparately: 'src_left'/'src_top' are the same for the luma and chroma. If the luma and chroma can be resized with the same subpixel shifts, use the resizer filters directly.")
        
        if isGray(clip):
            raise ValueError("ResizeSeparately: 'clip' is GRAY. Use the resizer filters directly.")

        if kernel not in ["Bilinear", "Bicubic", "Lanczos", "Spline16", "Spline36"]:
            raise ValueError("ResizeSeparately: 'kernel' must be 'Bilinear', 'Bicubic', 'Lanczos', 'Spline16', 'Spline36'.")
        
        if cplace not in ["MPEG1", "MPEG2"]:
            raise ValueError("ResizeSeparately: 'cplace' must be 'MPEG1' or 'MPEG2'.")
        
        
        width = [width, width >> clip.format.subsampling_w, width >> clip.format.subsampling_w]
        height = [height, height >> clip.format.subsampling_h, height >> clip.format.subsampling_h]
        
        
        src_left[1] = src_left[1] / (1 << clip.format.subsampling_w)
            
        if clip.format.subsampling_w == 1 and cplace == "MPEG2":
            MPEG2shift = 0.25 * (1.0 - clip.width / width[0])
            
            src_left[1] += MPEG2shift
                
        src_top[1] = src_top[1] / (1 << clip.format.subsampling_h)
            
        src_left.append(src_left[1])
        src_top.append(src_top[1])
            
        
        planes = [None, None, None]
        
        for plane in range(3):
            p = core.std.ShufflePlanes(clips=clip, planes=plane, colorfamily=vs.GRAY)
            
            p = eval("core.resize." + kernel)(clip=p,
                                              width=width[plane],
                                              height=height[plane],
                                              src_left=src_left[plane],
                                              src_top=src_top[plane])
            
            planes[plane] = p
            
        return core.std.ShufflePlanes(clips=planes, planes=[0, 0, 0], colorfamily=clip.format.color_family)
        
        


    if not isinstance(clip, vs.VideoNode):
        raise ValueError("xaa: 'clip' must be a clip.")
        
    iw = clip.width
    ih = clip.height
    
    if clip.width == 0 or clip.height == 0:
        raise RuntimeError("xaa: 'clip' must have constant dimensions.")
    
    
    ow = Default(ow, iw)
    oh = Default(oh, ih)
    
    
    if mode[0:2] in ["dr", "di"]:
        ss = Default(ss, 1.0)
    elif mode == "maa2":
        mode = "sr SangNom"
        
        mtype = Default(mtype, "Sobel")
        mthr = Default(mthr, 7.0)
    elif mode == "daa":
        mode = "drv znedi3"
        
        ss = Default(ss, 1.0)
        csharp = Default(csharp, 1)
        mask = Default(mask, 0)
        chroma = Default(chroma, 1)
    elif mode in ["Mrdaa", "MrdaaLame"]:
        mode = "null"
        
        uscl = Default(uscl, "znedi3")
        csharp = Default(csharp, 2)
        cstr = Default(cstr, 1.0)
        mask = Default(mask, 0)
        chroma = Default(chroma, 1)
    elif mode == "santiag":
        mode = "di2 znedi3"
        
        ss = Default(ss, 1.0)
        mask = Default(mask, 0)
        chroma = Default(chroma, 1)


    ss = Default(ss, 2.0)
    ssw = Default(ssw, ss)
    ssh = Default(ssh, ss)
    uscl = Default(uscl, "Spline36")
    csharp = Default(csharp, 0)
    cstr = Default(cstr, -1.0)
    mask = Default(mask, 1)
    mtype = Default(mtype, "TEdgeMask")
    mthr = Default(mthr, 8.0)
    chroma = Default(chroma, 0)
        
    if ow == 0 or oh == 0:
        raise ValueError("xaa: 'ow' and 'oh' cannot be 0.")
    
    if ss <= 0 or ssw <= 0 or ssh <= 0:
        raise ValueError("xaa: 'ss', 'ssw', and 'ssh' must be greater than 0.")

    acceptable_dscl = ["Bilinear", "Bicubic", "Point", "Lanczos", "Spline16", "Spline36"]
    if dscl not in acceptable_dscl:
        raise ValueError("xaa: 'dscl' must be one of {}.".format(acceptable_dscl))
    
    acceptable_uscl = acceptable_dscl + ["znedi3", "nnedi3cl", "eedi3", "eedi2", "eedi3 nnedi3cl", "eedi3 znedi3", "eedi3 eedi2"]
    if uscl not in acceptable_uscl:
        raise ValueError("xaa: 'uscl' must be one of {}.".format(acceptable_uscl))
    
    if mask > 2:
        raise ValueError("xaa: 'mask' must be 0, 1, 2, or a negative number.")
    
    if csharp not in [0, 1, 2]:
        raise ValueError("xaa: 'csharp' must be 0, 1, or 2.")
    
    if cplace not in ["MPEG1", "MPEG2"]:
        raise ValueError("xaa: 'cplace' must be 'MPEG1' or 'MPEG2'.")
    
    if clip.format is None:
        raise RuntimeError("xaa: 'clip' must have constant format.")
    
    
    ##### Set variable values based on parameter settings #####
    
    # Translate the cplace parameter into values understood by the VapourSynth resizers.
    if cplace == "MPEG1":
        chromaloc = "center"
    elif cplace == "MPEG2":
        chromaloc = "left"
    
    
    if clip.format.sample_type != vs.INTEGER or clip.format.bits_per_sample > 16:
        raise RuntimeError("xaa: 'clip' must have 8..16 bit integer format.")
    
    if not (isGray(clip) or is420(clip) or is422(clip) or is444(clip)):
        raise RuntimeError("xaa: 'clip' must be GRAY, 420, 422, or 444.")
    
    
    hssc12 = clip.format.subsampling_w > 0
    vssc12 = clip.format.subsampling_h > 0
    
    if ow > 0 and hssc12 and ow % 2:
        raise ValueError("xaa: output width of {} must be a multiple of 2.".format(clip.format.name))
    
    if oh > 0 and vssc12 and oh % 2:
        raise ValueError("xaa: output height of {} must be a multiple of 2.".format(clip.format.name))
    
    if isGray(clip):
        chroma = 0
        
    if chroma not in [0, 1, 2]:
        raise ValueError("xaa: 'chroma' must be 0, 1, or 2.")
    
    if chroma == 0:
        planes = [0]
    else:
        planes = [0, 1, 2]

    
    # If ssw or ssh is a float, use it as a multiplier to determine the supersampled resolution
    if isinstance(ssw, float):
        if ssw == 1.0:
            ssw = iw
        else:
            ssw = int(AvisynthRound(iw * ssw / 4.0) * 4)
    elif not isinstance(ssw, int):
        raise TypeError("xaa: 'ssw' must be a float or int.")
        
    if isinstance(ssh, float):
        if ssh == 1.0:
            ssh = ih
        else:
            ssh = int(AvisynthRound(ih * ssh / 4.0) * 4)
    elif not isinstance(ssh, int):
        raise TypeError("xaa: 'ssh' must be a float or int.")
    
    
    # Output at the supersampled resolution if the output width or height is negative
    if ow < 0 or oh < 0:
        ow = ssw
        oh = ssh
        
        
    # Make a copy of the mode parameter to use in error messages.
    original_mode = mode
        
    
    if mode == "null":
        aa_mode = "null"
    elif mode[0:2] in ["sr", "dr", "di"]:
        aa_mode = mode[0:2]
        mode = mode[2:]
    else:
        raise ValueError("xaa: invalid mode string '{}': the antialiasing mode must be 'sr', 'dr', or 'di'.".format(original_mode))
    
    # Remove spacers from the mode string
    mode_separators = [" ", "_", "+", "-"]
    if mode[0] in mode_separators:
        mode = mode[1:]
    
    aa_h = True
    aa_v = True
    
    # Get the aa direction from the mode string
    if mode[0] == "b":
        mode = mode[1:]
    elif mode[0] == "h":
        aa_v = False
        mode = mode[1:]
    elif mode[0] == "v":
        aa_h = False
        mode = mode[1:]
        
    if mode[0] in mode_separators:
        mode = mode[1:]
        
    digits = "0123456789"
    
    # Get the number of aa passes from the mode string
    if mode[0] in digits:
        aa_pass = int(mode[0])
        mode = mode[1:]
        
        if aa_pass == 0:
            raise ValueError("xaa: the number of aa passes must be greater than 0.")
    else:
        aa_pass = 1
    
    if mode[0] in mode_separators:
        mode = mode[1:]
        
    # Get the aa type from the mode string
    if mode == "null":
        aa_type = "null"
    elif mode.startswith("SangNom"):
        aa_type = "SangNom"
    elif mode.startswith("nnedi3cl"):
        aa_type = "nnedi3cl"
    elif mode.startswith("znedi3"):
        aa_type = "znedi3"
    elif mode.startswith("eedi3"):
        aa_type = "eedi3"
    elif mode.startswith("eedi2"):
        aa_type = "eedi2"
    else:
        raise ValueError("xaa: invalid mode string '{}': the antialiasing type must be 'SangNom', 'nnedi3cl', 'znedi3', 'eedi3', or 'eedi2'.".format(original_mode))
    
    # Get the aa sclip from the mode string
    if aa_type == "eedi3" and len(mode) > 5:
        mode = mode[5:]
        
        if mode[0] in mode_separators:
            mode = mode[1:]
            
        aa_sclip = mode
        
        acceptable_aa_sclip = acceptable_dscl + ["SangNom", "znedi3", "nnedi3cl", "eedi2"]
        if aa_sclip not in acceptable_aa_sclip:
            raise ValueError("xaa: invalid mode string '{}': the antialiasing sclip type must be one of {}.".format(original_mode, acceptable_aa_sclip))
    else:
        aa_sclip = ""
    
    
    # Get the sclip setting for eedi3 upscaling from the uscl string
    if uscl.startswith("eedi3") and len(uscl) > 5:
        rs_sclip = uscl[5:]
        uscl = "eedi3"
        
        if rs_sclip[0] in mode_separators:
            rs_sclip = rs_sclip[1:]
    else:
        rs_sclip = ""
        
    
    # Define these before the resize sections so they can be used as conditionals
    # TODO this comment might have been necessary only in Avisynth
    if aa_mode == "di" and csharp != 1 and not aa_v:
        aa_ow = ssw * 2
    else:
        aa_ow = ssw
        
    if aa_mode == "di" and csharp != 1 and aa_v:
        aa_oh = ssh * 2
    else:
        aa_oh = ssh
        
    if ssw > iw or ssh > ih:
        rs1_type = uscl
    else:
        rs1_type = dscl
    rs1_isedi = "edi" in rs1_type
    
    if ow > aa_ow or oh > aa_oh:
        rsaa_type = uscl
    else:
        rsaa_type = dscl
    rsaa_isedi = "edi" in rsaa_type
    
    if ow > iw or oh > ih:
        rs2_type = uscl
    else:
        rs2_type = dscl
    rs2_isedi = "edi" in rs2_type
    
    
    # Override the csharp setting if cstr=0, or if csharp=1 and mode="null" since it won't have any effect in that case.
    if cstr == 0 or (csharp == 1 and aa_mode == "null"):
        csharp = 0
        
    # Override the cstr setting if csharp=0 since it won't be used.
    if csharp == 0:
        cstr = 0
        
    # Get TEdgeMask's type parameter from the mtype string if present, or otherwise default to type 4
    if mtype.startswith("TEdgeMask") and len(mtype) > len("TEdgeMask") + 1:
        raise ValueError("xaa: TEdgeMask type must be a single character.")
    
    if mtype.startswith("TEdgeMask") and len(mtype) > len("TEdgeMask"):
        temtype = int(mtype[len("TEdgeMask")])
        mtype = "TEdgeMask"
        if temtype < 1 or temtype > 5:
            raise ValueError("xaa: TEdgeMask type must be between 1 and 5.")
    else:
        temtype = 4
        
    acceptable_mtype = ["TEdgeMask", "TCanny", "Prewitt", "Sobel"]
    if mtype not in acceptable_mtype:
        raise ValueError("xaa: 'mtype' must be one of {}.".format(acceptable_mtype))
    
    if mthr <= 0.0:
        raise ValueError("xaa: 'mthr' must be greater than 0.")
    
        
    
    # Round the mthr values for Prewitt and Sobel mask types
    if mtype not in ["TEdgeMask", "TCanny"]:
        mthr = AvisynthRound(mthr)
        eedimthr = AvisynthRound(eedimthr)
        
        
    # Remove frame properties that could confuse nnedi3 etc or the resizer.
    clip = core.std.SetFrameProp(clip=clip, prop="_FieldBased", delete=True)
    clip = core.std.SetFrameProp(clip=clip, prop="_Field", delete=True)
    
    
    ##### Scale the input clip to the supersampled resolution #####
    
    # rs1_type and rs1_isedi are defined earlier
    if ssw > iw * 6 - 4:
        rs1_rfacX = 8
    elif ssw > iw * 3 - 4:
        rs1_rfacX = 4
    elif ssw > iw:
        rs1_rfacX = 2
    else:
        rs1_rfacX = 1
        
    if ssh > ih * 6 - 4:
        rs1_rfacY = 8
    elif ssh > ih * 3 - 4:
        rs1_rfacY = 4
    elif ssh > ih:
        rs1_rfacY = 2
    else:
        rs1_rfacY = 1
    
    if ssw >= iw * rs1_rfacX or ssh >= ih * rs1_rfacY:
        rs1_cshift = "Spline36"
    else:
        rs1_cshift = dscl
        
    
    # To avoid resizing twice, don't correct the edi_rpow2 center shift until
    # resizing to the output resolution if no other processing will happen until then.
    # This isn't done all the time because the center shift messes with antialiasing.
    delay_cshift = aa_mode == "null" and rs1_isedi and ssw == iw * rs1_rfacX and ssh == ih * rs1_rfacY
    
    if delay_cshift and rs1_isedi and rs1_rfacX > 1:
        if not hssc12 or chroma == 0:
            rs1_hshift = -0.5
        else:
            rs1_hshift = -0.5 * (rs1_rfacX - 1)
    else:
        rs1_hshift = 0
        
    if delay_cshift and rs1_isedi and rs1_rfacY > 1:
        rs1_vshift = -0.5
    else:
        rs1_vshift = 0
        
    if delay_cshift and rs1_isedi and rs1_rfacX > 1 and cplace == "MPEG1" and hssc12 and chroma:
        rs1_hshift_c = -0.5 * (rs1_rfacX - 1) + rs1_hshift
    else:
        rs1_hshift_c = rs1_hshift
        
    if delay_cshift and rs1_isedi and rs1_rfacY > 1 and vssc12 and chroma:
        rs1_vshift_c = rs1_vshift * 2.0
    else:
        rs1_vshift_c = rs1_vshift
        
    
    # both as in both horizontal (3x1) and vertical (1x3)
    mt_expand_mode_both = [0, 1, 0,
                           1,    1,
                           0, 1, 0]
    
    # Edge mask for eedi3's mclip parameter to use for the rs1 and rs2 resizes
    if uscl == "eedi3" and eedimthr > 0:
        if mtype == "TEdgeMask":
            rs12_mclip = clip.tedgemask.TEdgeMask(threshold=eedimthr, type=temtype, link=0, planes=planes)
        elif mtype == "TCanny":
            rs12_mclip = clip.tcanny.TCanny(t_h=eedimthr, t_l=eedimthr, planes=planes, op=0)
            rs12_mclip = rs12_mclip.std.Maximum(planes=planes, coordinates=mt_expand_mode_both).std.Inflate(planes=planes)
            rs12_mclip = rs12_mclip.std.Minimum(planes=planes, coordinates=mt_expand_mode_both)
        elif mtype == "Prewitt":
            # Add 1 to obtain the behaviour of mt_edge's thX1/thX2 parameters:
            # mt_edge does pixel <= mthr ? 0 : 255
            # But we use std.Binarize which does pixel < mthr ? 0 : 255
            rs12_mclip = clip.std.Prewitt(planes=planes).std.Binarize(threshold=(eedimthr + 1) << (clip.format.bits_per_sample - 8), planes=planes)
        elif mtype == "Sobel":
            rs12_mclip = clip.std.Sobel(planes=planes).std.Binarize(threshold=(eedimthr + 1) << (clip.format.bits_per_sample - 8), planes=planes)
        
        rs12_mclip = rs12_mclip.std.Inflate(planes=planes)
    else:
        rs12_mclip = None
        
        
    if chroma == 0:
        clip_y8 = core.std.ShufflePlanes(clips=clip, planes=0, colorfamily=vs.GRAY)
    else:
        clip_y8 = clip
        
        
    if ssw == iw and ssh == ih:
        rs1 = clip_y8
    elif rs1_isedi:
        edi_params = dict(clip=clip_y8, rfactorX=rs1_rfacX, rfactorY=rs1_rfacY, edi=rs1_type, cplace=cplace,
                          alpha=eediA, beta=eediB, gamma=eediG, sclip=rs_sclip, mclip=rs12_mclip)
        if delay_cshift:
            edi_params.update(dict(YV12cfix=False))
        else:
            edi_params.update(dict(cshift=rs1_cshift, fwidth=ssw, fheight=ssh))
            
        rs1 = edi_rpow2(**edi_params)
    else:
        rs1 = eval("core.resize." + rs1_type)(clip=clip_y8, width=ssw, height=ssh, chromaloc_s=chromaloc, chromaloc_in_s=chromaloc)
    
    
    ##### Apply antialiasing to the supersampled clip #####
    
    # To avoid resizing twice, don't downscale the aaclip after di antialiasing unless needed for csharp=1.
    aa_delayresize_h = aa_mode == "di" and csharp != 1 and not aa_v
    aa_delayresize_v = aa_mode == "di" and csharp != 1 and aa_v
    
    if aa_delayresize_h:
        aa_hshift = -0.5
    else:
        aa_hshift = 0
    
    if aa_delayresize_v:
        aa_vshift = -0.5
    else:
        aa_vshift = 0
        
    if aa_delayresize_h and hssc12 and chroma and cplace == "MPEG1":
        aa_hshift_c = -0.5 + aa_hshift
    else:
        aa_hshift_c = aa_hshift
    
    if aa_delayresize_v and vssc12 and chroma:
        aa_vshift_c = aa_vshift * 2.0
    else:
        aa_vshift_c = aa_vshift
        
        
    # Pad the frame with rows of duplicate pixels to avoid errors from
    # mod1 resolutions and edge distortion caused by deinterlacing.
    rs1_ismod4 = ssw % 4 == 0 and ssh % 4 == 0
    rs1_ismod8 = ssw % 8 == 0 and ssh % 8 == 0
    rs1_pad8 = (not rs1_ismod8 and aa_type == "eedi2" and hssc12 and not is420(clip) and chroma) or \
               (not rs1_ismod8 and aa_type == "eedi3" and hssc12 and not is420(clip) and chroma and aa_sclip not in ["", "SangNom", "znedi3", "nnedi3cl"])
    
    
    # Don't add padding when using di eedi3 antialiasing unless it's
    # needed for mod4/mod8 compatibility because it doesn't distort edges.
    rs1_addpad = not (aa_mode == "null" or (aa_mode == "di" and aa_type == "eedi3" and rs1_ismod4 and not rs1_pad8))
    
    if rs1_pad8:
        rs1_padR = 8 - ssw % 8
        rs1_padT = 8 - ssh % 8
    else:
        rs1_padR = 4 - ssw % 4
        rs1_padT = 4 - ssh % 4
    
    if rs1_padR < 4:
        rs1_padR += 4
        
    if rs1_padT < 4:
        rs1_padT += 4
        
    if rs1_pad8 and (ssw + rs1_padR + 4) % 8 == 0:
        rs1_padL = 4
    elif rs1_pad8:
        rs1_padL = 8
    else:
        rs1_padL = 4
        
    if rs1_pad8 and (ssh + rs1_padT + 4) % 8 == 0:
        rs1_padB = 4
    elif rs1_pad8:
        rs1_padB = 8
    else:
        rs1_padB = 4
        
    
    ssw_pad = ssw
    ssh_pad = ssh
    if rs1_addpad:
        ssw_pad += rs1_padR + rs1_padL
        ssh_pad += rs1_padT + rs1_padB
    
    if hssc12:
        ssw_pad_c = ssw_pad // 2
    else:
        ssw_pad_c = ssw_pad
    
    if vssc12:
        ssh_pad_c = ssh_pad // 2
    else:
        ssh_pad_c = ssh_pad
        
    
    # Edge mask for eedi3's mclip parameter to use for antialiasing
    aa_mclip = None
    aa_mclipv = None
    aa_mcliph = None
    
    if eedimthr > 0:
        if mtype == "TEdgeMask":
            aa_mclip = rs1.tedgemask.TEdgeMask(threshold=eedimthr, type=temtype, link=0, planes=planes)
        elif mtype == "TCanny":
            aa_mclip = rs1.tcanny.TCanny(t_h=eedimthr, t_l=eedimthr, planes=planes, op=0)
            aa_mclip = aa_mclip.std.Maximum(planes=planes, coordinates=mt_expand_mode_both).std.Inflate(planes=planes)
            aa_mclip = aa_mclip.std.Minimum(planes=planes, coordinates=mt_expand_mode_both)
        elif mtype == "Prewitt":
            aa_mclip = rs1.std.Prewitt(planes=planes).std.Binarize(threshold=(eedimthr + 1) << (rs1.format.bits_per_sample - 8), planes=planes)
        elif mtype == "Sobel":
            aa_mclip = rs1.std.Sobel(planes=planes).std.Binarize(threshold=(eedimthr + 1) << (rs1.format.bits_per_sample - 8), planes=planes)
        
        aa_mclip = aa_mclip.std.Inflate(planes=planes)
        
        if rs1_addpad:
            aa_mclip_pad = aa_mclip.resize.Point(width=ssw + rs1_padL + rs1_padR,
                                                 height=ssh + rs1_padT + rs1_padB,
                                                 src_left=-rs1_padL,
                                                 src_top=-rs1_padT,
                                                 src_width=ssw + rs1_padL + rs1_padR,
                                                 src_height=ssh + rs1_padT + rs1_padB)
        else:
            aa_mclip_pad = aa_mclip
            
        aa_mclipv = aa_mclip_pad
        aa_mcliph = aa_mclipv.std.Transpose()


    if rs1_addpad:
        rs1_pad = rs1.resize.Point(width=ssw + rs1_padL + rs1_padR,
                                   height=ssh + rs1_padT + rs1_padB,
                                   src_left=-rs1_padL,
                                   src_top=-rs1_padT,
                                   src_width=ssw + rs1_padL + rs1_padR,
                                   src_height=ssh + rs1_padT + rs1_padB)
    else:
        rs1_pad = rs1
        
    
    # Perform antialiasing
    if aa_mode == "null":
        aaclip = rs1
    elif (aa_type != "SangNom" and not is422(clip)) or (aa_type != "SangNom" and is420(clip) and chroma):
        # When using SangNom2, it's faster to split the planes into Y8 clips and process them separately
        # TODO Is it? Why?
        
        aaclip = rs1_pad
        
        if aa_h:
            aaclip = aaclip.std.Transpose()

            if aa_mode == "sr":
                aaclip = xaa_sr(aaclip, aa_type, aa_pass, cplace, 48, nns, eediA, eediB, eediG, aa_sclip, aa_mcliph)
            elif aa_mode == "dr":
                aaclip = xaa_dr(aaclip, aa_type, aa_pass, cplace, 48, nns, eediA, eediB, eediG, aa_sclip, aa_mcliph)
            elif aa_mode == "di":
                aaclip = xaa_di(aaclip, aa_type, aa_pass, cplace, 48, nns, eediA, eediB, eediG, aa_sclip, aa_mcliph)
            
                if not aa_delayresize_h:
                    if vssc12 and chroma:
                        aaclip = ResizeSeparately(clip=aaclip,
                                                  width=ssh_pad,
                                                  height=ssw_pad,
                                                  src_left=[0, 0],
                                                  src_top=[-0.5, -1.0],
                                                  kernel=dscl,
                                                  cplace=cplace)
                    else:
                        aaclip = eval("core.resize." + dscl)(clip=aaclip,
                                                             width=ssh_pad,
                                                             height=ssw_pad,
                                                             src_left=0,
                                                             src_top=-0.5,
                                                             chromaloc_s=chromaloc,
                                                             chromaloc_in_s=chromaloc)
        
            aaclip = aaclip.std.Transpose()

        if aa_v:
            if aa_mode == "sr":
                aaclip = xaa_sr(aaclip, aa_type, aa_pass, cplace, 48, nns, eediA, eediB, eediG, aa_sclip, aa_mclipv)
            elif aa_mode == "dr":
                aaclip = xaa_dr(aaclip, aa_type, aa_pass, cplace, 48, nns, eediA, eediB, eediG, aa_sclip, aa_mclipv)
            elif aa_mode == "di":
                aaclip = xaa_di(aaclip, aa_type, aa_pass, cplace, 48, nns, eediA, eediB, eediG, aa_sclip, aa_mclipv)
                
                if not aa_delayresize_v:
                    if vssc12 and chroma:
                        aaclip = ResizeSeparately(clip=aaclip,
                                                  width=ssw_pad,
                                                  height=ssh_pad,
                                                  src_left=[0, 0],
                                                  src_top=[-0.5, -1.0],
                                                  kernel=dscl,
                                                  cplace=cplace)
                    else:
                        aaclip = eval("core.resize." + dscl)(clip=aaclip,
                                                             width=ssw_pad,
                                                             height=ssh_pad,
                                                             src_left=0,
                                                             src_top=-0.5,
                                                             chromaloc_s=chromaloc,
                                                             chromaloc_in_s=chromaloc)
    else:
        snaa_plane = [48, 0, 0]
        ssw_pad_plane = [ssw_pad, ssw_pad_c, ssw_pad_c]
        ssh_pad_plane = [ssh_pad, ssh_pad_c, ssh_pad_c]
        aaclip_plane = [None, None, None]
        
        for plane in range(rs1_pad.format.num_planes):
            aaclip_plane[plane] = core.std.ShufflePlanes(clips=rs1_pad, planes=plane, colorfamily=vs.GRAY)
            
            if aa_mcliph is not None:
                aa_mcliph_plane = core.std.ShufflePlanes(clips=aa_mcliph, planes=plane, colorfamily=vs.GRAY)
            else:
                aa_mcliph_plane = None
                
            if aa_mclipv is not None:
                aa_mclipv_plane = core.std.ShufflePlanes(clips=aa_mclipv, planes=plane, colorfamily=vs.GRAY)
            else:
                aa_mclipv_plane = None
        
            if aa_h:
                aaclip_plane[plane] = aaclip_plane[plane].std.Transpose()

                if aa_mode == "sr":
                    aaclip_plane[plane] = xaa_sr(aaclip_plane[plane], aa_type, aa_pass, cplace, snaa_plane[plane], nns, eediA, eediB, eediG, aa_sclip, aa_mcliph_plane)
                elif aa_mode == "dr":
                    aaclip_plane[plane] = xaa_dr(aaclip_plane[plane], aa_type, aa_pass, cplace, snaa_plane[plane], nns, eediA, eediB, eediG, aa_sclip, aa_mcliph_plane)
                elif aa_mode == "di":
                    aaclip_plane[plane] = xaa_di(aaclip_plane[plane], aa_type, aa_pass, cplace, snaa_plane[plane], nns, eediA, eediB, eediG, aa_sclip, aa_mcliph_plane)
                    
                    if not aa_delayresize_h:
                        aaclip_plane[plane] = eval("core.resize." + dscl)(clip=aaclip_plane[plane],
                                                                          width=ssh_pad_plane[plane],
                                                                          height=ssw_pad_plane[plane],
                                                                          src_left=0,
                                                                          src_top=-0.5)
                    
                aaclip_plane[plane] = aaclip_plane[plane].std.Transpose()
                
            if aa_v:
                if aa_mode == "sr":
                    aaclip_plane[plane] = xaa_sr(aaclip_plane[plane], aa_type, aa_pass, cplace, snaa_plane[plane], nns, eediA, eediB, eediG, aa_sclip, aa_mclipv_plane)
                elif aa_mode == "dr":
                    aaclip_plane[plane] = xaa_dr(aaclip_plane[plane], aa_type, aa_pass, cplace, snaa_plane[plane], nns, eediA, eediB, eediG, aa_sclip, aa_mclipv_plane)
                elif aa_mode == "di":
                    aaclip_plane[plane] = xaa_di(aaclip_plane[plane], aa_type, aa_pass, cplace, snaa_plane[plane], nns, eediA, eediB, eediG, aa_sclip, aa_mclipv_plane)
                    
                    if not aa_delayresize_v:
                        aaclip_plane[plane] = eval("core.resize." + dscl)(clip=aaclip_plane[plane],
                                                                          width=ssw_pad_plane[plane],
                                                                          height=ssh_pad_plane[plane],
                                                                          src_left=0,
                                                                          src_top=-0.5)
        if rs1_pad.format.num_planes == 1:
            aaclip = aaclip_plane[0]
        else:
            aaclip = core.std.ShufflePlanes(clips=aaclip_plane, planes=[0, 0, 0], colorfamily=rs1_pad.format.color_family)
        
    
    # Crop the padding off
    if rs1_addpad:
        if aa_delayresize_h:
            aaclip = aaclip.std.Crop(left=rs1_padL * 2, top=rs1_padT, right=rs1_padR * 2, bottom=rs1_padB)
        elif aa_delayresize_v:
            aaclip = aaclip.std.Crop(left=rs1_padL, top=rs1_padT * 2, right=rs1_padR, bottom=rs1_padB * 2)
        else:
            aaclip = aaclip.std.Crop(left=rs1_padL, top=rs1_padT, right=rs1_padR, bottom=rs1_padB)
            
    
    ##### Apply contra-sharpening before scaling to the output resolution if csharp=1 #####

            

    
    if csharp == 1:
        aadiff = core.std.MakeDiff(clipa=rs1, clipb=aaclip, planes=planes)
        if cstr < 0:
            aablur = core.rgvs.RemoveGrain(clip=aaclip, mode=11)
        else:
            aablur = Blur(clip=aaclip, amount=cstr * 0.2)
        sharpdiff = core.std.MakeDiff(clipa=aaclip, clipb=aablur, planes=planes)
        repaired = core.rgvs.Repair(clip=sharpdiff, repairclip=aadiff, mode=13)
        aaclip = core.std.MergeDiff(clipa=aaclip, clipb=repaired, planes=planes)
    
    
    ##### Scale the antialiased clip to the output resolution #####
    
    # rsaa_type and rsaa_isedi are defined earlier
    if ow > aa_ow * 6 - 4:
        rsaa_rfacX = 8
    elif ow > aa_ow * 3 - 4:
        rsaa_rfacX = 4
    elif ow > aa_ow:
        rsaa_rfacX = 2
    else:
        rsaa_rfacX = 1
        
    if oh > aa_oh * 6 - 4:
        rsaa_rfacY = 8
    elif oh > aa_oh * 3 - 4:
        rsaa_rfacY = 4
    elif oh > aa_oh:
        rsaa_rfacY = 2
    else:
        rsaa_rfacY = 1
        
    if ow >= aa_ow * rsaa_rfacX or oh >= aa_oh * rsaa_rfacY:
        rsaa_cshift = "Spline36"
    else:
        rsaa_cshift = dscl
        
    
    # Center shift values for the rsaa resize if edi_rpow2 is used
    if rsaa_isedi and rsaa_rfacX > 1:
        if not hssc12 or chroma == 0:
            rsaa_hshift = -0.5
        else:
            rsaa_hshift = -0.5 * (rsaa_rfacX - 1)
    else:
        rsaa_hshift = 0
        
    if rsaa_isedi and rsaa_rfacY > 1:
        rsaa_vshift = -0.5
    else:
        rsaa_vshift = 0
        
    if rsaa_isedi and rsaa_rfacX > 1 and cplace == "MPEG1" and hssc12 and chroma:
        rsaa_hshift_c = -0.5 * (rsaa_rfacX - 1) + rsaa_hshift
    else:
        rsaa_hshift_c = rsaa_hshift
        
    if rsaa_isedi and rsaa_rfacY > 1 and vssc12 and chroma:
        rsaa_vshift_c = rsaa_vshift * 2.0
    else:
        rsaa_vshift_c = rsaa_vshift
        
    # Add center shift corrections from rs1 delay_cshift and aa_delayresize to the rsaa corrections
    if rsaa_isedi:
        rsaa_hshift = rsaa_hshift + rs1_hshift * rsaa_rfacX + aa_hshift * rsaa_rfacX
        rsaa_vshift = rsaa_vshift + rs1_vshift * rsaa_rfacY + aa_vshift * rsaa_rfacY
        rsaa_hshift_c = rsaa_hshift_c + rs1_hshift_c * rsaa_rfacX + aa_hshift_c * rsaa_rfacX
        rsaa_vshift_c = rsaa_vshift_c + rs1_vshift_c * rsaa_rfacY + aa_vshift_c * rsaa_rfacY
    else:
        rsaa_hshift = rs1_hshift + aa_hshift
        rsaa_vshift = rs1_vshift + aa_vshift
        rsaa_hshift_c = rs1_hshift_c + aa_hshift_c
        rsaa_vshift_c = rs1_vshift_c + aa_vshift_c
        
    rsaa_UVshift = rsaa_hshift != rsaa_hshift_c or rsaa_vshift != rsaa_vshift_c
    
    
    # Reuse the eedi3 mclip mask from antialiasing
    if uscl == "eedi3" and eedimthr > 0:
        rsaa_mclip = aa_mclip
    else:
        rsaa_mclip = None
        
    
    aaclip_y8 = aaclip
        
        
    if ow == aa_ow and oh == aa_oh and not delay_cshift and not aa_delayresize_h and not aa_delayresize_v:
        rsaa = aaclip_y8
    elif rsaa_isedi and (delay_cshift or aa_delayresize_h or aa_delayresize_v):
        rsaa = aaclip_y8
        rsaa = edi_rpow2(clip=rsaa, rfactorX=rsaa_rfacX, rfactorY=rsaa_rfacY, edi=rsaa_type, cplace=cplace, YV12cfix=False, alpha=eediA, beta=eediB, gamma=eediG, sclip=rs_sclip, mclip=rsaa_mclip)
        if rsaa_UVshift:
            rsaa = ResizeSeparately(clip=rsaa,
                                    width=ow,
                                    height=oh,
                                    src_left=[rsaa_hshift, rsaa_hshift_c],
                                    src_top=[rsaa_vshift, rsaa_vshift_c],
                                    kernel=rsaa_cshift,
                                    cplace=cplace)
        else:
            rsaa = eval("core.resize." + rsaa_cshift)(clip=rsaa,
                                                      width=ow,
                                                      height=oh,
                                                      src_left=rsaa_hshift,
                                                      src_top=rsaa_vshift,
                                                      chromaloc_in_s=chromaloc,
                                                      chromaloc_s=chromaloc)
    elif rsaa_isedi:
        rsaa = aaclip_y8
        rsaa = edi_rpow2(clip=rsaa, rfactorX=rsaa_rfacX, rfactorY=rsaa_rfacY, edi=rsaa_type, cshift=rsaa_cshift, fwidth=ow, fheight=oh, cplace=cplace, alpha=eediA, beta=eediB, gamma=eediG, sclip=rs_sclip, mclip=rsaa_mclip)
    else:
        if rsaa_UVshift:
            rsaa = ResizeSeparately(clip=aaclip_y8,
                                    width=ow,
                                    height=oh,
                                    src_left=[rsaa_hshift, rsaa_hshift_c],
                                    src_top=[rsaa_vshift, rsaa_vshift_c],
                                    kernel=rsaa_cshift,
                                    cplace=cplace)
        else:
            rsaa = eval("core.resize." + rsaa_cshift)(clip=aaclip_y8,
                                                      width=ow,
                                                      height=oh,
                                                      src_left=rsaa_hshift,
                                                      src_top=rsaa_vshift,
                                                      chromaloc_in_s=chromaloc,
                                                      chromaloc_s=chromaloc)
            
    
    # Make sure the rsaa clip has the same chroma sampling as the input
    # rsaa is either the same format as the input clip (when chroma is not 0), or it is GRAY (when chroma is 0)
    if rsaa.format.id != clip.format.id:
        rsaa = core.resize.Bicubic(clip=rsaa, format=clip.format.id)
    
    
    ##### Scale the input clip to the output resolution without antialiasing for masking and chroma #####
    
    if ow > iw * 6 - 4:
        rs2_rfacX = 8
    elif ow > iw * 3 - 4:
        rs2_rfacX = 4
    elif ow > iw:
        rs2_rfacX = 2
    else:
        rs2_rfacX = 1
        
    if oh > ih * 6 - 4:
        rs2_rfacY = 8
    elif oh > ih * 3 - 4:
        rs2_rfacY = 4
    elif oh > ih:
        rs2_rfacY = 2
    else:
        rs2_rfacY = 1
        
    if ow >= iw * rs2_rfacX and oh >= ih * rs2_rfacY:
        rs2_cshift = "Spline36"
    else:
        rs2_cshift = dscl
        
    
    if ow == iw and oh == ih:
        rs2 = clip
    elif rs2_isedi:
        rs2 = clip
        # The Avisynth version had rfactorY=rs1_rfacY and rs2_rfacY was never used.
        rs2 = edi_rpow2(clip=rs2, rfactorX=rs2_rfacX, rfactorY=rs2_rfacY, edi=rs2_type, cshift=rs2_cshift, fwidth=ow, fheight=oh, cplace=cplace, alpha=eediA, beta=eediB, gamma=eediG, sclip=rs_sclip, mclip=rs12_mclip)
    else:
        rs2 = eval("core.resize." + rs2_type)(clip=clip,
                                              width=ow,
                                              height=oh,
                                              chromaloc_in_s=chromaloc,
                                              chromaloc_s=chromaloc)
        
    
    
    
    
    ##### Apply contra-sharpening after scaling to the output resolution if csharp=2 #####
    
    if csharp == 2:
        UVrg = 11 if chroma else -1
        UVrp = 13 if chroma else -1
        
        aadiff = core.std.MakeDiff(clipa=rs2, clipb=rsaa, planes=planes)
        if cstr < 0:
            aablur = core.rgvs.RemoveGrain(clip=rsaa, mode=[11, UVrg, UVrg])
        else:
            aablur = Blur(clip=rsaa, amount=cstr * 0.2)
        sharpdiff = core.std.MakeDiff(clipa=rsaa, clipb=aablur, planes=planes)
        repaired = core.rgvs.Repair(clip=sharpdiff, repairclip=aadiff, mode=[13, UVrp, UVrp])
        rsaa = core.std.MergeDiff(clipa=rsaa, clipb=repaired, planes=planes)
        
    
    ##### Masking, chroma merging, and output #####
    
    # Reuse the eedi3 mclip mask from the rs1 and rs2 resizes if it's the same
    if rs12_mclip is not None and mthr == eedimthr and iw == ow and ih == oh:
        emask = rs12_mclip
    else:
        if mtype == "TEdgeMask":
            emask = rs2.tedgemask.TEdgeMask(threshold=mthr, type=temtype, link=0, planes=planes)
        elif mtype == "TCanny":
            emask = rs2.tcanny.TCanny(t_h=mthr, t_l=mthr, planes=planes, op=0)
            emask = emask.std.Maximum(planes=planes, coordinates=mt_expand_mode_both).std.Inflate(planes=planes)
            emask = emask.std.Minimum(planes=planes, coordinates=mt_expand_mode_both)
        elif mtype == "Prewitt":
            emask = rs2.std.Prewitt(planes=planes).std.Binarize(threshold=(mthr + 1) << (rs2.format.bits_per_sample - 8), planes=planes)
        elif mtype == "Sobel":
            emask = rs2.std.Sobel(planes=planes).std.Binarize(threshold=(mthr + 1) << (rs2.format.bits_per_sample - 8), planes=planes)
            
        emask = emask.std.Inflate(planes=planes)
    
    
    # 8-bit version of the rs2 clip for masking
    # TODO why can't you make the overlay in the same format as the input clip?
    # TODO okay, you can't do it in GRAY because it can't be green, but what's the reason to convert 422?
    rs2_yv24 = rs2.resize.Bicubic(format=core.register_format(color_family=vs.YUV,
                                                              sample_type=rs2.format.sample_type,
                                                              bits_per_sample=rs2.format.bits_per_sample,
                                                              subsampling_w=0,
                                                              subsampling_h=0))
        
    if isGray(clip) or is422(clip):
        # TODO why doesn't YUV420P8 need this?
        eover = rs2_yv24
        overlay = rs2_yv24
    else:
        eover = rs2
        overlay = rs2
    eover = core.std.Expr(clips=eover, expr=["", "x 2 /"])
    overlay = core.std.MaskedMerge(clipa=overlay, clipb=eover, mask=core.std.ShufflePlanes(clips=emask, planes=0, colorfamily=vs.GRAY), first_plane=True)
    
    if is422(clip):
        overlay = overlay.resize.Bicubic(format=core.register_format(color_family=overlay.format.color_family,
                                                                     sample_type=overlay.format.sample_type,
                                                                     bits_per_sample=overlay.format.bits_per_sample,
                                                                     subsampling_w=1,
                                                                     subsampling_h=0))
        
    
    if chroma == 0:
        merge_planes = [0]
    elif chroma == 1:
        merge_planes = [0, 1, 2]
    elif chroma == 2:
        merge_planes = [1, 2]
    
    if mask == 0:
        if isGray(clip) or chroma == 1:
            merged = rsaa
        elif chroma == 0:
            merged = core.std.ShufflePlanes(clips=[rsaa, rs2, rs2], planes=[0, 1, 2], colorfamily=rsaa.format.color_family)
        elif chroma == 2:
            merged = core.std.ShufflePlanes(clips=[rs2, rsaa, rsaa], planes=[0, 1, 2], colorfamily=rsaa.format.color_family)
    elif mask == 1:
        merged = core.std.MaskedMerge(clipa=rs2, clipb=rsaa, mask=emask, planes=merge_planes)
    elif mask == 2:
        merged = core.std.MaskedMerge(clipa=rsaa, clipb=rs2, mask=emask, planes=merge_planes)
        
        if chroma == 0:
            merged = core.std.ShufflePlanes(clips=[merged, rs2, rs2], planes=[0, 1, 2], colorfamily=merged.format.color_family)
        elif chroma == 2:
            merged = core.std.ShufflePlanes(clips=[rs2, merged, merged], planes=[0, 1, 2], colorfamily=merged.format.color_family)
    
    
    if mask < 0:
        output = overlay
    else:
        output = merged
        
    return output


##### Recursive functions for multipass antialiasing #####
# TODO move these functions inside xaa
# maybe?

def xaa_sr(clip, type="SangNom", passes=1, cplace="MPEG2", snaa=48, nns=1, alpha=0.2, beta=0.25, gamma=20.0, sclip="", mclip=None, f=1):
    core = vs.get_core()

    iw = clip.width
    ih = clip.height
    
    # Alternate the field every pass, starting with 1 by default
    field = f % 2
    
    if field == 1:
        snfield = 1
    else:
        snfield = 2
        
    if clip.format.num_planes > 1:
        snaa = [snaa, 0, 0]
        
    # SeparateFields will throw an error from mod2 heights if the input is YV12,
    # so don't define sf unless it's needed, in which case the resolution will have been padded to mod4.
    pad8 = type == "eedi2" or (type == "eedi3" and sclip not in ["", "SangNom", "znedi3", "nnedi3cl"])
    
    if pad8:
        sf = clip.std.SeparateFields(tff=True).std.SetFrameProp(prop="_Field", delete=True)
        if field == 1:
            sf = sf.std.SelectEvery(cycle=2, offsets=0)
        else:
            sf = sf.std.SelectEvery(cycle=2, offsets=1)
    else:
        sf = None
        
    # Use a src_top shift dependent on the field when resizing for the sclip to keep it in alignment with the eedi3 clip.
    # Additionally, the vertical shift for YV12 chroma is doubled, so the chroma must be resized separately.
    if field == 1:
        rshift = 0.25
    else:
        rshift = -0.25
    
        
    if sclip == "":
        sclip2 = None
    elif sclip == "SangNom":
        sclip2 = clip.sangnom.SangNom(order=snfield, aa=snaa)
    elif sclip == "znedi3":
        sclip2 = clip.znedi3.nnedi3(field=field, nns=nns)
    elif sclip == "nnedi3cl":
        sclip2 = clip.nnedi3cl.NNEDI3CL(field=field, nns=nns)
    elif sclip == "eedi2":
        sclip2 = sf.eedi2.EEDI2(field=field)
    elif is420(clip):
        sclip2 = ResizeSeparately(clip=sf,
                                  width=iw,
                                  height=ih,
                                  src_left=[0, 0],
                                  src_top=[rshift, rshift * 2],
                                  kernel=sclip,
                                  cplace=cplace)
    else:
        sclip2 = eval("core.resize." + sclip)(clip=sf,
                                              width=iw,
                                              height=ih,
                                              src_left=0,
                                              src_top=rshift,
                                              chromaloc_in_s=chromaloc,
                                              chromaloc_s=chromaloc)
        
    
    if type == "SangNom":
        aa = clip.sangnom.SangNom(order=snfield, aa=snaa)
    elif type == "znedi3":
        aa = clip.znedi3.nnedi3(field=field, nns=nns)
    elif type == "nnedi3cl":
        aa = clip.nnedi3cl.NNEDI3CL(field=field, nns=nns)
    elif type == "eedi3":
        aa = clip.eedi3m.EEDI3(field=field, alpha=alpha, beta=beta, gamma=gamma, sclip=sclip2, mclip=mclip)
    elif type == "eedi2":
        aa = sf.eedi2.EEDI2(field=field)
    else:
        raise ValueError("xaa_sr: invalid antialiasing type '{}'.".format(type))
    
    if passes > 0:
        return xaa_sr(clip=aa, type=type, passes=passes - 1, cplace=cplace, snaa=snaa, nns=nns, alpha=alpha, beta=beta, gamma=gamma, sclip=sclip, mclip=mclip, f=f + 1)
    else:
        return clip
    


def xaa_dr(clip, type="znedi3", passes=1, cplace="MPEG2", snaa=48, nns=1, alpha=0.2, beta=0.25, gamma=20.0, sclip="", mclip=None):
    core = vs.get_core()

    iw = clip.width
    ih = clip.height
    
    if clip.format.num_planes > 1:
        snaa = [snaa, 0, 0]
    
    pad8 = type == "eedi2" or (type == "eedi3" and sclip not in ["", "SangNom", "znedi3", "nnedi3cl"])
    
    if pad8:
        sf = clip.std.SeparateFields(tff=True).std.SetFrameProp(prop="_Field", delete=True)
        tf = sf.std.SelectEvery(cycle=2, offsets=0)
        bf = sf.std.SelectEvery(cycle=2, offsets=1)
    else:
        sf = None
        tf = None
        bf = None
        
    if sclip == "":
        sclip2 = None
    elif sclip == "SangNom":
        sclip2 = core.std.Interleave(clips=[core.sangnom.SangNom(clip=clip, order=1, aa=snaa),
                                            core.sangnom.SangNom(clip=clip, order=2, aa=snaa)])
    elif sclip == "znedi3":
        sclip2 = clip.znedi3.nnedi3(field=3, nns=nns)
    elif sclip == "nnedi3cl":
        sclip2 = clip.nnedi3cl.NNEDI3CL(field=3, nns=nns)
    elif sclip == "eedi2":
        sclip2 = sf.eedi2.EEDI2(field=3)
    elif is420(clip):
        sclip2 = core.std.Interleave(clips=[ResizeSeparately(clip=tf,
                                                             width=iw,
                                                             height=ih,
                                                             src_left=[0, 0],
                                                             src_top=[0.25, 0.5],
                                                             kernel=sclip,
                                                             cplace=cplace),
                                            ResizeSeparately(clip=bf,
                                                             width=iw,
                                                             height=ih,
                                                             src_left=[0, 0],
                                                             src_top=[-0.25, -0.5],
                                                             kernel=sclip,
                                                             cplace=cplace)])
    else:
        sclip2 = core.std.Interleave(clips=[eval("core.resize." + sclip)(clip=tf,
                                                                         width=iw,
                                                                         height=ih,
                                                                         src_left=0,
                                                                         src_top=0.25,
                                                                         chromaloc_in_s=chromaloc,
                                                                         chromaloc_s=chromaloc),
                                            eval("core.resize." + sclip)(clip=bf,
                                                                         width=iw,
                                                                         height=ih,
                                                                         src_left=0,
                                                                         src_top=-0.25,
                                                                         chromaloc_in_s=chromaloc,
                                                                         chromaloc_s=chromaloc)])
    
    
    if type == "SangNom":
        aa = core.std.Interleave(clips=[core.sangnom.SangNom(clip=clip, order=1, aa=snaa),
                                        core.sangnom.SangNom(clip=clip, order=2, aa=snaa)])
    elif type == "znedi3":
        aa = clip.znedi3.nnedi3(field=3, nns=nns)
    elif type == "nnedi3cl":
        aa = clip.nnedi3cl.NNEDI3CL(field=3, nns=nns)
    elif type == "eedi3":
        aa = clip.eedi3m.EEDI3(field=3, alpha=alpha, beta=beta, gamma=gamma, sclip=sclip2, mclip=mclip)
    elif type == "eedi2":
        aa = sf.eedi2.EEDI2(field=3)
    else:
        raise ValueError("xaa_dr: invalid antialiasing type '{}'.".format(type))
    
    aa = core.std.Merge(clipa=aa.std.SelectEvery(cycle=2, offsets=0),
                        clipb=aa.std.SelectEvery(cycle=2, offsets=1),
                        weight=0.5)
    
    if passes > 0:
        return xaa_dr(clip=aa, type=type, passes=passes - 1, cplace=cplace, snaa=snaa, nns=nns, alpha=alpha, beta=beta, gamma=gamma, sclip=sclip, mclip=mclip)
    else:
        return clip

    
    
def xaa_di(clip, type="znedi3", passes=1, cplace="MPEG2", snaa=48, nns=1, alpha=0.2, beta=0.25, gamma=20.0, sclip="", mclip=None, f=1, dh=True):
    core = vs.get_core()

    # Translate the cplace parameter into values understood by the VapourSynth resizers.
    if cplace == "MPEG1":
        chromaloc = "center"
    elif cplace == "MPEG2":
        chromaloc = "left"

    iw = clip.width
    ih = clip.height
    
    # Alternate the field every pass, starting with 1.
    # Don't change the f value from the default or else the center shift correction will be wrong.
    field = f % 2
    
    if field == 1:
        snfield = 1
    else:
        snfield = 2
        
    if clip.format.num_planes > 1:
        snaa = [snaa, 0, 0]
        
    pad8 = type == "eedi2" or (type == "eedi3" and sclip not in ["", "SangNom", "znedi3", "nnedi3cl"])
    
    if pad8:
        sf = clip.std.SeparateFields(tff=True).std.SetFrameProp(prop="_Field", delete=True)
        if field == 1:
            sf = sf.std.SelectEvery(cycle=2, offsets=0)
        else:
            sf = sf.std.SelectEvery(cycle=2, offsets=1)
    else:
        sf = None
        
    if field == 1:
        rshift = 0.25
    else:
        rshift = -0.25
        
    if sclip == "":
        sclip2 = None
    elif sclip == "SangNom":
        sclip2 = clip
        if dh:
            sclip2 = core.resize.Point(clip=sclip2, width=iw, height=ih * 2, chromaloc_in_s=chromaloc, chromaloc_s=chromaloc)
        sclip2 = sclip2.sangnom.SangNom(order=snfield, aa=snaa)
    elif sclip == "znedi3":
        sclip2 = clip.znedi3.nnedi3(field=field, dh=dh, nns=nns)
    elif sclip == "nnedi3cl":
        sclip2 = clip.nnedi3cl.NNEDI3CL(field=field, dh=dh, nns=nns)
    elif sclip == "eedi2":
        if dh:
            sclip2 = clip.eedi2.EEDI2(field=field)
        else:
            sclip2 = sf.eedi2.EEDI2(field=field)
    elif is420(clip):
        if dh:
            sclip2 = ResizeSeparately(clip=clip,
                                      width=iw,
                                      height=ih * 2,
                                      src_left=[0, 0],
                                      src_top=[rshift, rshift * 2],
                                      kernel=sclip,
                                      cplace=cplace)
        else:
            sclip2 = ResizeSeparately(clip=sf,
                                      width=iw,
                                      height=ih * 2,
                                      src_left=[0, 0],
                                      src_top=[rshift, rshift * 2],
                                      kernel=sclip,
                                      cplace=cplace)
    else:
        if dh:
            sclip2 = eval("core.resize." + sclip)(clip=clip,
                                              width=iw,
                                              height=ih * 2,
                                              src_left=0,
                                              src_top=rshift,
                                              chromaloc_in_s=chromaloc,
                                              chromaloc_s=chromaloc)
        else:
            sclip2 = eval("core.resize." + sclip)(clip=sf,
                                              width=iw,
                                              height=ih,
                                              src_left=0,
                                              src_top=rshift,
                                              chromaloc_in_s=chromaloc,
                                              chromaloc_s=chromaloc)
            
    
    # The height is only doubled on the first pass
    if type == "SangNom":
        aa = clip
        if dh:
            aa = core.resize.Point(clip=aa,
                                   width=iw,
                                   height=ih * 2,
                                   chromaloc_in_s=chromaloc,
                                   chromaloc_s=chromaloc)
        aa = aa.sangnom.SangNom(order=snfield, aa=snaa)
    elif type == "znedi3":
        aa = clip.znedi3.nnedi3(field=field, dh=dh, nns=nns)
    elif type == "nnedi3cl":
        aa = clip.nnedi3cl.NNEDI3CL(field=field, dh=dh, nns=nns)
    elif type == "eedi3":
        aa = clip.eedi3m.EEDI3(field=field, dh=dh, alpha=alpha, beta=beta, gamma=gamma, sclip=sclip2, mclip=mclip)
    elif type == "eedi2":
        if dh:
            aa = clip.eedi2.EEDI2(field=field)
        else:
            aa = sf.eedi2.EEDI2(field=field)
    else:
        raise ValueError("xaa_di: invalid antialiasing type '{}'.".format(type))


    # Double the height of the mclip for passes after the first.
    if mclip is not None and dh:
        if is420(clip):
            mclip = ResizeSeparately(clip=mclip,
                                     width=iw,
                                     height=ih * 2,
                                     src_left=[0, 0],
                                     src_top=[0.25, 0.5],
                                     kernel="Spline36",
                                     cplace=cplace)
        else:
            mclip = core.resize.Spline36(clip=mclip,
                                         width=iw,
                                         height=ih * 2,
                                         src_left=0,
                                         src_top=0.25,
                                         chromaloc_in_s=chromaloc,
                                         chromaloc_s=chromaloc)
        
        mclip = mclip.std.Binarize(planes=planes)
        
    if passes > 0:
        return xaa_di(clip=aa, type=type, passes=passes - 1, cplace=cplace, snaa=snaa, nns=nns, alpha=alpha, beta=beta, gamma=gamma, sclip=sclip, mclip=mclip, f=f + 1, dh=False)
    else:
        return clip
