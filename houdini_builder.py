# -*- coding: utf-8 -*-
"""
Houdini Startup Script for Points & Reality 3DGS Pipeline
유저의 추출된 전체 네트워크 데이터(위치, 와이어링 포함)를 기반으로 100% 똑같이 복제합니다.
"""

import sys
import os
import hou
import hdefereval

# 유저가 추출한 완벽한 노드 네트워크 데이터 (위치 및 선 연결 정보 포함)
NODE_DATA = [
    {
        "Node_Name": "polyfill1",
        "Node_Type": "polyfill",
        "Position": [-8.15631, -15.6073],
        "Inputs": [{"index": 0, "node": "clip2"}],
        "Parameters": {}
    },
    {
        "Node_Name": "clip2",
        "Node_Type": "clip::2.0",
        "Position": [-8.15631, -14.6073],
        "Inputs": [{"index": 0, "node": "sphere1"}],
        "Parameters": {"dirx": 0.0, "diry": 1.0}
    },
    {
        "Node_Name": "sphere1",
        "Node_Type": "sphere",
        "Position": [-8.15631, -13.6073],
        "Inputs": [],
        "Parameters": {"type": 2, "radx": 0.5, "rady": 0.5, "radz": 0.5, "scale": 3.0}
    },
    {
        "Node_Name": "delete1",
        "Node_Type": "delete",
        "Position": [-6.66331, -18.163],
        "Inputs": [{"index": 0, "node": "group1"}],
        "Parameters": {"group": "group1", "negate": 1, "entity": 1}
    },
    {
        "Node_Name": "group1",
        "Node_Type": "groupcreate",
        "Position": [-6.66331, -17.1366],
        "Inputs": [{"index": 0, "node": "transform1"}, {"index": 1, "node": "polyfill1"}],
        "Parameters": {"grouptype": 1, "groupbase": 0, "groupbounding": 1, "boundtype": 2}
    },
    {
        "Node_Name": "org_hou",
        "Node_Type": "null",
        "Position": [-4.8325, -1.8882],
        "Inputs": [{"index": 0, "node": "bakegsplat1"}],
        "Parameters": {}
    },
    {
        "Node_Name": "org_ply",
        "Node_Type": "null",
        "Position": [-4.8325, 0.0418],
        "Inputs": [{"index": 0, "node": "file1"}],
        "Parameters": {}
    },
    {
        "Node_Name": "attribtransfer1",
        "Node_Type": "attribtransfer",
        "Position": [-3.23127, -9.36723],
        "Inputs": [{"index": 0, "node": "pack1"}, {"index": 1, "node": "extracttransform1"}],
        "Parameters": {"pointattriblist": "transform", "threshold": 0}
    },
    {
        "Node_Name": "box_clip1",
        "Node_Type": "labs::box_clip",
        "Position": [-3.22782, -17.4974],
        "Inputs": [{"index": 0, "node": "transform1"}, {"index": 1, "node": "box1"}],
        "Parameters": {"disable": 1}
    },
    {
        "Node_Name": "transform1",
        "Node_Type": "xform",
        "Position": [-3.22782, -13.6337],
        "Inputs": [{"index": 0, "node": "unpack1"}],
        "Parameters": {"tx": 1.282, "ty": -0.45, "tz": 0.4, "ry": 8.5}
    },
    {
        "Node_Name": "unpack1",
        "Node_Type": "unpack",
        "Position": [-3.22782, -12.416],
        "Inputs": [{"index": 0, "node": "transformbyattrib1"}],
        "Parameters": {}
    },
    {
        "Node_Name": "transformbyattrib1",
        "Node_Type": "xformbyattrib",
        "Position": [-3.22782, -11.0327],
        "Inputs": [{"index": 0, "node": "attribtransfer1"}],
        "Parameters": {"xformattrib": "transform", "updateaffectednmls": 0}
    },
    {
        "Node_Name": "switch1",
        "Node_Type": "switch",
        "Position": [-3.22782, -33.3048],
        "Inputs": [{"index": 0, "node": "box_clip1"}, {"index": 1, "node": "groupdelete1"}],
        "Parameters": {"input": 1}
    },
    {
        "Node_Name": "modified_ply",
        "Node_Type": "null",
        "Position": [-3.22782, -34.4671],
        "Inputs": [{"index": 0, "node": "switch1"}],
        "Parameters": {}
    },
    {
        "Node_Name": "for_SSplat",
        "Node_Type": "xform",
        "Position": [-3.22782, -36.3017],
        "Inputs": [{"index": 0, "node": "modified_ply"}],
        "Parameters": {"rz": 180.0}
    },
    {
        "Node_Name": "pack1",
        "Node_Type": "pack",
        "Position": [-3.13422, -6.44],
        "Inputs": [{"index": 0, "node": "bakegsplat1"}],
        "Parameters": {"viewportlod": 3}
    },
    {
        "Node_Name": "bakegsplat1",
        "Node_Type": "bakegsplat",
        "Position": [-2.8325, -0.615],
        "Inputs": [{"index": 0, "node": "file1"}],
        "Parameters": {"sphcoeff": 1}
    },
    {
        "Node_Name": "file1",
        "Node_Type": "file",
        "Position": [-2.8325, 1.1445],
        "Inputs": [],
        "Parameters": {"file": "D:/SPLATIAL/GS_datas/Lou_scan.ply"}
    },
    {
        "Node_Name": "extracttransform1",
        "Node_Type": "extracttransform",
        "Position": [-1.32702, -7.6784],
        "Inputs": [{"index": 0, "node": "remesh1"}, {"index": 1, "node": "reorient"}],
        "Parameters": {"outputattribs": 2}
    },
    {
        "Node_Name": "attribwrangle2",
        "Node_Type": "attribwrangle",
        "Position": [-1.03856, -37.3935],
        "Inputs": [{"index": 0, "node": "for_SSplat"}],
        "Parameters": {
            "class": 0,
            "snippet": "// 1. 대용량의 주범인 SH(빛 반사) 데이터 삭제 (초경량 웹 뷰어용)\nremovepointattrib(0, \"GS_SPH_R\");\nremovepointattrib(0, \"GS_SPH_G\");\nremovepointattrib(0, \"GS_SPH_B\");\n\n// 2. Karma 렌더러 임시 찌꺼기 속성 삭제\nremovedetailattrib(0, \"xn__karmaobjectrendervisibility_0kbg\");"
        }
    },
    {
        "Node_Name": "Manual_Selection",
        "Node_Type": "groupcreate",
        "Position": [-1.03556, -27.9006],
        "Inputs": [{"index": 0, "node": "isolated1"}],
        "Parameters": {
            "groupname": "Manual_Selection",
            "grouptype": 1,
            "basegroup": "3360 3394 3694 19020-19022 19110 22129-22131 48363 49204-49210 56707 56713-56716 56718-56723 56732-56737 56744-56750 56755-56767 68172 71583-71585 81812 116630-116631 116729-116749 116929 116999 124488-124489 124573 124594-124595 124688-124690 124719 125176 125201-125215 125327 125356 125384 127637-127639 127657-127659 130420 130426-130429 135254 137456-137464 137592-137598 139136 139184 142025 143111 143113 143116 143124 143127 143131 143144 143149 143172 143497-143501 145613 147228 147237-147244 148933-148941 150680 150687 151315-151329 151332-151343 151897-151910 156519-156520 157767 159357-159361 159363-159365 159827-159834 159914 161693 162769-162770 162780 166211-166214 166216-166221 168756 171914-171915 173458 173694-173741 174382-174416 174420 174458 174463 174501 175009-175015 175066 175069 175074-175077 175079 175087 175094-175095 175100-175102 177642-177645 178969 178978 178986 178997-179063 179473 180421 182083-182088"
        }
    },
    {
        "Node_Name": "isolated2",
        "Node_Type": "blast",
        "Position": [-1.03556, -30.026],
        "Inputs": [{"index": 0, "node": "Manual_Selection"}],
        "Parameters": {"group": "Manual_Selection"}
    },
    {
        "Node_Name": "groupdelete1",
        "Node_Type": "groupdelete",
        "Position": [-1.03556, -31.6972],
        "Inputs": [{"index": 0, "node": "isolated2"}],
        "Parameters": {"selection_folder": 1}
    },
    {
        "Node_Name": "Exporter",
        "Node_Type": "python",
        "Position": [-1.03556, -38.6933],
        "Inputs": [{"index": 0, "node": "attribwrangle2"}],
        "Parameters": {
            "python": "# PYTHON SOP: export Houdini-native Gaussian Splats to spec 3DGS .ply\n#             WITH spherical-harmonic re-orientation (\"SH bake\").\n#\n# Wire your edited splats into input 0.\n#\n# Spare parms (Gear menu > Edit Parameter Interface):\n#   outfile    - File   type, name: outfile\n#   srgb       - Toggle type, name: srgb   (ON if Bake GSplats linearized color)\n#   writeply   - Button type, name: writeply\n#                Callback Script (Language: Python):\n#                  kwargs['node'].geometry(); hou.session.gs_ply_export(kwargs['node'])\n#\n# Nothing is written on cook. Only the button writes.\n# -------------------------------------------------------------------------\n\nimport hou\n\ndef gs_ply_export(node):\n    \"\"\"Called by the writeply button callback, not on cook.\"\"\"\n    import hou\n    import numpy as np\n\n    # --- Constants ---\n    DELTA_TOL = 1e-4\n    IDENT_TOL = 1e-6\n    SH_C0 = 0.28209479177387814\n    SRGB_ENCODE = True\n\n    PROPS = [\"x\", \"y\", \"z\",\n             \"nx\", \"ny\", \"nz\",\n             \"f_dc_0\", \"f_dc_1\", \"f_dc_2\",\n             \"opacity\",\n             \"scale_0\", \"scale_1\", \"scale_2\",\n             \"rot_0\", \"rot_1\", \"rot_2\", \"rot_3\"]\n\n    C1 = 0.4886025119029199\n    C2 = [1.0925484305920792, -1.0925484305920792, 0.31539156525252005,\n         -1.0925484305920792, 0.5462742152960396]\n    C3 = [-0.5900435899266435, 2.890611442640554, -0.4570457994644658,\n           0.3731763325901154, -0.4570457994644658, 1.445305721320277,\n          -0.5900435899266435]\n    BANDS = [slice(1, 4), slice(4, 9), slice(9, 16)]\n\n    # --- Helper Functions ---\n    def qmul(a, b):\n        ax, ay, az, aw = a[..., 0], a[..., 1], a[..., 2], a[..., 3]\n        bx, by, bz, bw = b[..., 0], b[..., 1], b[..., 2], b[..., 3]\n        return np.stack([aw*bx + ax*bw + ay*bz - az*by,\n                         aw*by - ax*bz + ay*bw + az*bx,\n                         aw*bz + ax*by - ay*bx + az*bw,\n                         aw*bw - ax*bx - ay*by - az*bz], -1)\n\n    def qconj(q):\n        return q * np.array([-1.0, -1.0, -1.0, 1.0])\n\n    def qnorm(q):\n        return q / np.linalg.norm(q, axis=-1, keepdims=True)\n\n    def quat_to_rotmat(q):\n        x, y, z, w = q\n        return np.array([[1-2*(y*y+z*z), 2*(x*y-w*z),   2*(x*z+w*y)],\n                         [2*(x*y+w*z),   1-2*(x*x+z*z), 2*(y*z-w*x)],\n                         [2*(x*z-w*y),   2*(y*z+w*x),   1-2*(x*x+y*y)]])\n\n    def sh_basis(d):\n        x, y, z = d[:, 0], d[:, 1], d[:, 2]\n        xx, yy, zz = x*x, y*y, z*z\n        xy, yz, xz = x*y, y*z, x*z\n        return np.stack([\n            np.full_like(x, SH_C0),\n            -C1*y, C1*z, -C1*x,\n            C2[0]*xy, C2[1]*yz, C2[2]*(2*zz-xx-yy), C2[3]*xz, C2[4]*(xx-yy),\n            C3[0]*y*(3*xx-yy), C3[1]*xy*z, C3[2]*y*(4*zz-xx-yy),\n            C3[3]*z*(2*zz-3*xx-3*yy), C3[4]*x*(4*zz-xx-yy),\n            C3[5]*z*(xx-yy), C3[6]*x*(xx-3*yy)], 1)\n\n    def sh_rotation_matrices(q_xyzw):\n        M = quat_to_rotmat(q_xyzw)\n        N = 400\n        i = np.arange(N)\n        phi = np.arccos(1 - 2*(i+0.5)/N)\n        th = np.pi*(1+5**0.5)*(i+0.5)\n        dirs = np.stack([np.sin(phi)*np.cos(th),\n                         np.sin(phi)*np.sin(th), np.cos(phi)], 1)\n        B = sh_basis(dirs)\n        Bp = sh_basis(dirs @ M)       \n        mats, worst_ortho, worst_resid = [], 0.0, 0.0\n        for sl in BANDS:\n            T = np.linalg.pinv(B[:, sl]) @ Bp[:, sl]\n            worst_ortho = max(worst_ortho, float(np.abs(T.T@T - np.eye(T.shape[0])).max()))\n            worst_resid = max(worst_resid, float(np.abs(B[:, sl]@T - Bp[:, sl]).max()))\n            mats.append(T)\n        return mats, (worst_ortho, worst_resid)\n\n    def linear_to_srgb(c):\n        a = np.abs(c)\n        s = np.where(a <= 0.0031308, 12.92 * a, 1.055 * a**(1.0/2.4) - 0.055)\n        return np.sign(c) * s\n\n    def build_ply_bytes(P, Cd, alpha, orient, scale, srgb_encode=False, sh_rest=None):\n        n = P.shape[0]\n        nx = np.zeros((n, 3), dtype=np.float32)\n        \n        col = linear_to_srgb(Cd) if srgb_encode else Cd\n        f_dc = (col - 0.5) / SH_C0\n        \n        opacity = alpha\n        scale_log = np.log(np.maximum(scale, 1e-10))\n        rot = orient[:, [3, 0, 1, 2]] \n        \n        props = list(PROPS)\n        blocks = [P, nx, f_dc]\n        \n        if sh_rest is not None:\n            blocks.append(sh_rest)\n            sh_props = [\"f_rest_%d\" % i for i in range(sh_rest.shape[1])]\n            idx = props.index(\"opacity\")\n            props[idx:idx] = sh_props\n            \n        blocks += [opacity.reshape(-1, 1), scale_log, rot]\n\n        data = np.concatenate(blocks, axis=1).astype(\"<f4\", copy=False)\n        if data.shape[1] != len(props):\n            raise RuntimeError(\"column/property mismatch; %d vs %d\" % (data.shape[1], len(props)))\n\n        header = [\"ply\", \"format binary_little_endian 1.0\", \"element vertex %d\" % n]\n        header += [\"property float %s\" % p for p in props]\n        header += [\"end_header\", \"\"]\n        return \"\\n\".join(header).encode(\"ascii\") + data.tobytes(order=\"C\")\n\n    # --- Main Execution ---\n    geo = node.geometry()\n    n = geo.intrinsicValue(\"pointcount\")\n    if n == 0:\n        raise hou.Error(\"no points on input\")\n\n    p = node.parm(\"outfile\")\n    if p is None:\n        raise hou.Error(\"add a File spare parm named 'outfile'\")\n    path = p.eval()\n    if not path:\n        raise hou.Error(\"outfile is empty\")\n\n    sp = node.parm(\"srgb\")\n    srgb = bool(sp.eval()) if sp is not None else SRGB_ENCODE\n\n    def grab(name, width):\n        if geo.findPointAttrib(name) is None:\n            raise hou.Error(\"missing point attribute: %s\" % name)\n        return np.array(geo.pointFloatAttribValues(name), dtype=np.float32).reshape(n, width)\n\n    def grab_any(name):\n        attr = geo.findPointAttrib(name)\n        if attr is None:\n            return None\n        return np.array(geo.pointFloatAttribValues(name), dtype=np.float32).reshape(n, attr.size())\n\n    P = grab(\"P\", 3)\n    Cd = grab(\"Cd\", 3)\n    alpha = grab(\"GS_Alpha\", 1).reshape(-1)\n    \n    orient = grab(\"orient\", 4)\n    scale = grab(\"scale\", 3)\n\n    sh_rest = None\n    notes = [\"srgb encode: %s\" % (\"on\" if srgb else \"off\")]\n    \n    INCLUDE_SH = True\n    chans = [grab_any(\"GS_SPH_R\"), grab_any(\"GS_SPH_G\"), grab_any(\"GS_SPH_B\")]\n    rest = grab_any(\"restorient\")\n    ROTATE_SH = (rest is not None)\n\n    if INCLUDE_SH and all(c is not None for c in chans):\n        if chans[0].shape[1] != 16:\n            notes.append(\"SH rotation: only implemented for degree 3, skipped\")\n        elif ROTATE_SH:\n            o = qnorm(orient.astype(np.float64))\n            r = qnorm(rest.astype(np.float64))\n            delta = qnorm(qmul(o, qconj(r)))         \n            sgn = np.sign(np.sum(delta * delta[0], -1))\n            sgn[sgn == 0] = 1\n            delta *= sgn[:, None]                    \n            dev = float(np.abs(delta - delta[0]).max())\n            \n            if dev > DELTA_TOL:\n                raise hou.Error(\"non-rigid orientation edit (per-point SH delta varies by %.4g > %.4g).\" % (dev, DELTA_TOL))\n            q = qnorm(delta.mean(0))\n            angle = float(np.degrees(2*np.arccos(np.clip(abs(q[3]), 0, 1))))\n            \n            if angle < IDENT_TOL:\n                notes.append(\"SH rotation: delta ~identity (%.2e deg), skipped\" % angle)\n            else:\n                (T1, T2, T3), (ortho, resid) = sh_rotation_matrices(q)\n                if ortho > 1e-6 or resid > 1e-6:\n                    raise hou.Error(\"SH rotation self-check failed (ortho=%.2e resid=%.2e)\" % (ortho, resid))\n                for c in chans:                \n                    c[:, 1:4] = c[:, 1:4] @ T1.T\n                    c[:, 4:9] = c[:, 4:9] @ T2.T\n                    c[:, 9:16] = c[:, 9:16] @ T3.T\n                notes.append(\"SH re-oriented: rigid %.3f deg about %s (fit ortho=%.1e resid=%.1e)\"\n                             % (angle, np.round(q[:3]/(np.linalg.norm(q[:3])+1e-12), 3), ortho, resid))\n\n        sh_rest = np.concatenate([c[:, 1:] for c in chans], axis=1)\n\n        col_eff = linear_to_srgb(Cd) if srgb else Cd\n        f_dc_ref = (col_eff - 0.5) / SH_C0\n        dc = np.stack([c[:, 0] for c in chans], axis=1)\n        dev = np.abs(dc - f_dc_ref)\n        notes.append(\"DC cross-check vs GS_SPH_*[0]: median %.3g, p95 %.3g, within 1e-2 %.1f%%\"\n                     % (np.median(dev), np.percentile(dev, 95), 100.0 * (dev < 1e-2).mean()))\n    \n    elif INCLUDE_SH and any(c is not None for c in chans):\n        notes.append(\"only some of GS_SPH_R/G/B present, skipping SH\")\n    else:\n        notes.append(\"no GS_SPH_R/G/B found, writing DC only (SH degree 0)\")\n\n    blob = build_ply_bytes(P, Cd, alpha, orient, scale, srgb_encode=srgb, sh_rest=sh_rest)\n    \n    with open(path, \"wb\") as f:\n        f.write(blob)\n\n    msg = \"wrote %d splats (%.1f MB) -> %s\" % (n, len(blob) / 1048576.0, path)\n    print(msg)\n    for t in notes:\n        print(\"  \" + t)\n    try:\n        hou.ui.setStatusMessage(msg)\n    except AttributeError:\n        pass                 \n    return path\n\n# register for the button callback\nhou.session.gs_ply_export = gs_ply_export\n\n# pass geometry through untouched in viewport\nnode = hou.pwd()\ngeo = node.geometry()",
            "outfile": "D:/SPLATIAL/GS_datas/output/lou_refine_v002.ply",
            "srgb": 1
        }
    },
    {
        "Node_Name": "isolated",
        "Node_Type": "blast",
        "Position": [-1.00446, -21.8457],
        "Inputs": [{"index": 0, "node": "search_isolated"}],
        "Parameters": {"group": "isolated"}
    },
    {
        "Node_Name": "search_advanced",
        "Node_Type": "attribwrangle",
        "Position": [-0.973356, -23.7223],
        "Inputs": [{"index": 0, "node": "isolated"}],
        "Parameters": {
            "snippet": "float radius = chf(\"search_radius\");\nint target_min = chi(\"target_min\");\nint target_max = chi(\"target_max\");\n\n// 필요한 최대 개수(target_max)까지만 탐색하여 과부하를 막습니다 (+1은 자기 자신).\nint neighbors[] = nearpoints(0, @P, radius, target_max + 2);\n\n// len() 함수로 길이를 잰 뒤, 자기 자신 1개를 빼서 순수 이웃 개수를 구합니다.\nint count = len(neighbors) - 1; \n\n// 이웃 개수가 설정한 Min ~ Max 범위 안에 들면 덩어리로 간주합니다.\nif (count >= target_min && count <= target_max) {\n    @group_small_groups = 1;\n}",
            "search_radius": 0.028,
            "target_min": 1,
            "target_max": 5
        }
    },
    {
        "Node_Name": "isolated1",
        "Node_Type": "blast",
        "Position": [-0.970356, -26.1795],
        "Inputs": [{"index": 0, "node": "search_advanced"}],
        "Parameters": {"group": "small_groups"}
    },
    {
        "Node_Name": "search_isolated",
        "Node_Type": "attribwrangle",
        "Position": [-0.90378, -19.7005],
        "Inputs": [{"index": 0, "node": "box_clip1"}],
        "Parameters": {
            "snippet": "float radius = chf(\"search_radius\");\n// 몇 개 이하일 때 고립된 것으로 간주할지 정하는 파라미터 추가 (예: 5)\nint min_neighbors = chi(\"min_neighbors\"); \n\n// 필요한 개수까지만 탐색하여 k-d 트리 연산 과부하를 막습니다.\nint neighbors[] = nearpoints(0, @P, radius, min_neighbors + 1);\n\n// 주변 포인트 개수가 지정한 임계값보다 적으면 노이즈(isolated)로 분류합니다.\nif (len(neighbors) <= min_neighbors) {\n    @group_isolated = 1;\n}",
            "search_radius": 0.025,
            "min_neighbors": 3
        }
    },
    {
        "Node_Name": "box1",
        "Node_Type": "box",
        "Position": [0.625908, -13.8063],
        "Inputs": [],
        "Parameters": {"type": 1, "ty": 0.5, "scale": 2.0, "divrate1": 2, "divrate2": 2, "divrate3": 2}
    },
    {
        "Node_Name": "reorient",
        "Node_Type": "attribwrangle",
        "Position": [0.63558, -6.2456],
        "Inputs": [{"index": 0, "node": "remesh1"}, {"index": 1, "node": "bound1"}],
        "Parameters": {
            "class": 0,
            "snippet": "// box basis: any corner + its 3 neighbours\nint nb[] = neighbours(1, 0);\nvector o = point(1, \"P\", 0);\nvector ax[];\nfloat len[];\n\nforeach (int n; nb) {\n    vector e = point(1, \"P\", n) - o;\n    append(ax, e);\n    append(len, length(e));\n}\n\nint ord[] = argsort(len);           // ascending\nvector up = normalize(ax[ord[0]]);  // shortest = plane normal\nvector fwd = normalize(ax[ord[2]]); // longest = strip direction\n\n// sign disambiguation against the mesh's own facing\nvector nsum = {0,0,0};\nfor (int i = 0; i < nprimitives(0); i++)\n    nsum += prim_normal(0, i, 0.5, 0.5);\nif (dot(up, normalize(nsum)) < 0) up = -up;\n\n// orthonormalize, force right-handed\nfwd = normalize(fwd - up * dot(fwd, up));\nvector side = cross(fwd, up);\n\nmatrix3 m = transpose(set(fwd, up, side));\nvector cen = getbbox_center(1);       // OBB center\n\n// --- 이미지에서 잘린 부분 완성 (포인트 재정렬 적용) ---\nfor (int i = 0; i < npoints(0); i++) {\n    vector p = point(0, \"P\", i);\n    setpointattrib(0, \"P\", i, (p - cen) * m);\n}"
        }
    },
    {
        "Node_Name": "remesh1",
        "Node_Type": "remesh::2.0",
        "Position": [0.63858, -3.9272],
        "Inputs": [{"index": 0, "node": "add1"}],
        "Parameters": {}
    },
    {
        "Node_Name": "add1",
        "Node_Type": "add",
        "Position": [0.66738, -2.9264],
        "Inputs": [{"index": 0, "node": "sort1"}],
        "Parameters": {"stdswitcher1": 1, "switcher1": 1, "closedall": 1}
    },
    {
        "Node_Name": "sort1",
        "Node_Type": "sort",
        "Position": [0.7251, -1.575],
        "Inputs": [{"index": 0, "node": "blast1"}],
        "Parameters": {"ptsort": 2, "pointreverse": 1}
    },
    {
        "Node_Name": "blast1",
        "Node_Type": "blast",
        "Position": [0.7251, -0.615],
        "Inputs": [{"index": 0, "node": "file1"}],
        "Parameters": {"group": "206493 208381 213970 224018", "grouptype": 3, "negate": 1}
    },
    {
        "Node_Name": "Preview",
        "Node_Type": "groupcreate",
        "Position": [0.882516, -21.2651],
        "Inputs": [{"index": 0, "node": "search_isolated"}],
        "Parameters": {"groupname": "group2", "grouptype": 1, "basegroup": "isolated"}
    },
    {
        "Node_Name": "Preview1",
        "Node_Type": "groupcreate",
        "Position": [0.882516, -25.3086],
        "Inputs": [{"index": 0, "node": "search_advanced"}],
        "Parameters": {"groupname": "group2", "grouptype": 1, "basegroup": "small_groups"}
    },
    {
        "Node_Name": "bound1",
        "Node_Type": "bound",
        "Position": [1.02738, -5.0504],
        "Inputs": [{"index": 0, "node": "remesh1"}],
        "Parameters": {}
    },
    {
        "Node_Name": "attribwrangle1",
        "Node_Type": "attribwrangle",
        "Position": [2.97685, -18.6058],
        "Inputs": [{"index": 0, "node": "box_clip1"}],
        "Parameters": {
            "snippet": "float radius = chf(\"search_radius\");\nint maxpts = chi(\"max_pts\");\n\nint neighbors[] = nearpoints(0, @P, radius, maxpts);\n\nint count = 0;\nforeach (int pt; neighbors) {\n    if (pt != @ptnum) count++;\n}\n\nif (count == 0) {\n    setpointgroup(0, \"isolated\", @ptnum, 1, \"set\");\n}",
            "search_radius": 0.015,
            "max_pts": 100
        }
    }
]

def build_cleanup_network(target_ply_path: str):
    print("=" * 50)
    print("Points & Reality 3DGS Controller: Building EXACT Original Network from Data...")
    print(f"Target File: {target_ply_path}")
    print("=" * 50)

    # 씬 강제 초기화
    hou.hipFile.clear(suppress_save_prompt=True)
    
    obj = hou.node('/obj')
    geo = obj.createNode('geo', 'Cleanup_3DGS')
    for child in geo.children(): child.destroy()

    nodes_dict = {}

    # 1. 노드 생성, 파라미터 적용 및 위치(Position) 지정
    for nd in NODE_DATA:
        name = nd["Node_Name"]
        ntype = nd["Node_Type"]
        pos = nd["Position"]
        parms = nd["Parameters"]

        try:
            n = geo.createNode(ntype, name)
            n.setPosition(pos)
            nodes_dict[name] = n
        except Exception as e:
            print(f"⚠️ Warning: Could not create node type {ntype} ({name}). Error: {e}")
            continue

        ptg = n.parmTemplateGroup()
        ptg_changed = False

        # 없는 파라미터(Spare Parameter) 생성 로직
        for k, v in parms.items():
            if n.parm(k) is None:
                if isinstance(v, float):
                    ptg.append(hou.FloatParmTemplate(k, k, 1))
                elif isinstance(v, int):
                    ptg.append(hou.IntParmTemplate(k, k, 1))
                else:
                    if k in ['snippet', 'python']:
                        ptg.append(hou.StringParmTemplate(k, k, 1, string_type=hou.stringParmType.StringEditor))
                    else:
                        ptg.append(hou.StringParmTemplate(k, k, 1))
                ptg_changed = True

        # Exporter 버튼 생성
        if name == "Exporter" and not ptg.find("writeply"):
            ptm_btn = hou.ButtonParmTemplate("writeply", "Export to PLY", script_callback="kwargs['node'].geometry(); hou.session.gs_ply_export(kwargs['node'])", script_callback_language=hou.scriptLanguage.Python)
            ptg.append(ptm_btn)
            ptg_changed = True

        if ptg_changed:
            n.setParmTemplateGroup(ptg)

        # 파라미터 값 주입 (타겟 경로 오버라이드)
        for k, v in parms.items():
            if name == "file1" and k == "file":
                v = target_ply_path
            if name == "Exporter" and k == "outfile":
                v = target_ply_path.replace('02_postshot_exports', '03_houdini_cleaned')
            
            parm = n.parm(k)
            if parm is not None:
                try:
                    parm.set(v)
                except Exception as e:
                    print(f"Failed to set parm {k} on {name}: {e}")

    # 2. JSON 데이터에 명시된 선 연결(Wiring) 정확히 수행
    for nd in NODE_DATA:
        name = nd["Node_Name"]
        inputs = nd.get("Inputs", [])
        
        if name not in nodes_dict:
            continue
            
        target_node = nodes_dict[name]
        
        for inp in inputs:
            idx = inp["index"]
            src_name = inp["node"]
            
            if src_name in nodes_dict:
                target_node.setInput(idx, nodes_dict[src_name])
            else:
                print(f"⚠️ Missing source node {src_name} for connection to {name}")

    # 3. 레이아웃 마무리 (자동 정렬하지 않고 추출된 원본 레이아웃을 존중)
    if "Exporter" in nodes_dict:
        nodes_dict["Exporter"].setDisplayFlag(True)
        nodes_dict["Exporter"].setRenderFlag(True)
        
    try:
        network_editor = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
        if network_editor:
            network_editor.homeToSelection()
    except:
        pass
        
    print("Cleanup Network Build Complete! Your EXACT Original Nodes are perfectly restored.")

if __name__ == "__main__":
    target_file = os.environ.get("POINTS_REALITY_TARGET_PLY", "") or os.environ.get("SPLATIAL_TARGET_PLY", "")
    
    if target_file and os.path.exists(target_file):
        hdefereval.executeDeferred(lambda: build_cleanup_network(target_file))
    else:
        print("No target file passed or file does not exist.")