import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

OMML_NS = 'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"'

def omml_r(text, bold=False, italic=True, normal=False):
    pr = ""
    if bold:
        pr += "<m:b/>"
    if not italic:
        pr += "<m:i m:val=\"off\"/>"
    if normal:
        pr += "<m:nor/>"
    rpr = f"<m:rPr>{pr}</m:rPr>" if pr else ""
    return f"<m:r>{rpr}<m:t>{text}</m:t></m:r>"

def omml_sub(base, sub):
    return f"<m:sSub><m:e>{base}</m:e><m:sub>{sub}</m:sub></m:sSub>"

def omml_sup(base, sup):
    return f"<m:sSup><m:e>{base}</m:e><m:sup>{sup}</m:sup></m:sSup>"

def omml_subsup(base, sub, sup):
    return f"<m:sSubSup><m:e>{base}</m:e><m:sub>{sub}</m:sub><m:sup>{sup}</m:sup></m:sSubSup>"

def omml_frac(num, den):
    return f"<m:f><m:num>{num}</m:num><m:den>{den}</m:den></m:f>"

def omml_delim(content, beg="(", end=")"):
    return f'<m:d><m:dPr><m:begChr m:val="{beg}"/><m:endChr m:val="{end}"/><m:grow/></m:dPr><m:e>{content}</m:e></m:d>'

def omml_nary(chr_val, sub_val="", sup_val="", e_val="", lim_loc="undOvr"):
    sub_tag = f"<m:sub>{sub_val}</m:sub>" if sub_val else "<m:sub/>"
    sup_tag = f"<m:sup>{sup_val}</m:sup>" if sup_val else "<m:sup/>"
    return f'<m:nary><m:naryPr><m:chr m:val="{chr_val}"/><m:limLoc m:val="{lim_loc}"/></m:naryPr>{sub_tag}{sup_tag}<m:e>{e_val}</m:e></m:nary>'

# 14 Equations Definitions in OMML
def get_equation_omml(eq_num):
    if eq_num == 1:
        # C_SOZ = (1 / |K_soz|) * \sum_{i \in K_soz} p_i
        left = omml_sub(omml_r("C"), omml_r("SOZ", normal=True)) + omml_r(" = ", italic=False)
        frac = omml_frac(omml_r("1", italic=False), omml_delim(omml_sub(omml_r("K"), omml_r("soz", normal=True)), "|", "|"))
        sum_sub = omml_r("i ∈ ", italic=False) + omml_sub(omml_r("K"), omml_r("soz", normal=True))
        sum_expr = omml_nary("∑", sub_val=sum_sub, e_val=omml_sub(omml_r("p", bold=True), omml_r("i")))
        return left + frac + omml_r(" ") + sum_expr

    elif eq_num == 2:
        # C_res = (1 / |K_res|) * \sum_{j \in K_res} p_j
        left = omml_sub(omml_r("C"), omml_r("res", normal=True)) + omml_r(" = ", italic=False)
        frac = omml_frac(omml_r("1", italic=False), omml_delim(omml_sub(omml_r("K"), omml_r("res", normal=True)), "|", "|"))
        sum_sub = omml_r("j ∈ ", italic=False) + omml_sub(omml_r("K"), omml_r("res", normal=True))
        sum_expr = omml_nary("∑", sub_val=sum_sub, e_val=omml_sub(omml_r("p", bold=True), omml_r("j")))
        return left + frac + omml_r(" ") + sum_expr

    elif eq_num == 3:
        # d_0 = || C_SOZ - C_res ||_2
        left = omml_sub(omml_r("d"), omml_r("0", italic=False)) + omml_r(" = ", italic=False)
        norm_inner = omml_sub(omml_r("C"), omml_r("SOZ", normal=True)) + omml_r(" - ", italic=False) + omml_sub(omml_r("C"), omml_r("res", normal=True))
        norm = omml_sub(omml_delim(norm_inner, "‖", "‖"), omml_r("2", italic=False))
        return left + norm

    elif eq_num == 4:
        # R_res = \max_{j \in K_res} || p_j - C_res ||_2
        left = omml_sub(omml_r("R"), omml_r("res", normal=True)) + omml_r(" = ", italic=False)
        max_sub = omml_r("j ∈ ", italic=False) + omml_sub(omml_r("K"), omml_r("res", normal=True))
        max_op = omml_sub(omml_r("max", normal=True), max_sub)
        norm_inner = omml_sub(omml_r("p", bold=True), omml_r("j")) + omml_r(" - ", italic=False) + omml_sub(omml_r("C"), omml_r("res", normal=True))
        norm = omml_sub(omml_delim(norm_inner, "‖", "‖"), omml_r("2", italic=False))
        return left + max_op + omml_r(" ") + norm

    elif eq_num == 5:
        # w_k(t) = P_k(t)^2 / \sum_{m=1}^N P_m(t)^2
        left = omml_sub(omml_r("w"), omml_r("k")) + omml_delim(omml_r("t")) + omml_r(" = ", italic=False)
        num = omml_sup(omml_sub(omml_r("P"), omml_r("k")) + omml_delim(omml_r("t")), omml_r("2", italic=False))
        sum_sub = omml_r("m=1", italic=False)
        sum_sup = omml_r("N")
        sum_e = omml_sup(omml_sub(omml_r("P"), omml_r("m")) + omml_delim(omml_r("t")), omml_r("2", italic=False))
        den = omml_nary("∑", sub_val=sum_sub, sup_val=sum_sup, e_val=sum_e)
        return left + omml_frac(num, den)

    elif eq_num == 6:
        # R(t) = \sum_{k=1}^N w_k(t) p_k
        left = omml_r("R", bold=True) + omml_delim(omml_r("t")) + omml_r(" = ", italic=False)
        sum_sub = omml_r("k=1", italic=False)
        sum_sup = omml_r("N")
        sum_e = omml_sub(omml_r("w"), omml_r("k")) + omml_delim(omml_r("t")) + omml_sub(omml_r("p", bold=True), omml_r("k"))
        return left + omml_nary("∑", sub_val=sum_sub, sup_val=sum_sup, e_val=sum_e)

    elif eq_num == 7:
        # v(t) = || R(t + \Delta t) - R(t) ||_2 / \Delta t
        left = omml_r("v") + omml_delim(omml_r("t")) + omml_r(" = ", italic=False)
        t_delta = omml_r("t + Δt", italic=False)
        norm_inner = omml_r("R", bold=True) + omml_delim(t_delta) + omml_r(" - ", italic=False) + omml_r("R", bold=True) + omml_delim(omml_r("t"))
        num = omml_sub(omml_delim(norm_inner, "‖", "‖"), omml_r("2", italic=False))
        den = omml_r("Δt", italic=False)
        return left + omml_frac(num, den)

    elif eq_num == 8:
        # v_mean = (1 / (T - 1)) * \sum_{t=1}^{T-1} v(t)
        left = omml_sub(omml_r("v"), omml_r("mean", normal=True)) + omml_r(" = ", italic=False)
        frac = omml_frac(omml_r("1", italic=False), omml_r("T - 1", italic=False))
        sum_sub = omml_r("t=1", italic=False)
        sum_sup = omml_r("T - 1", italic=False)
        sum_e = omml_r("v") + omml_delim(omml_r("t"))
        return left + frac + omml_r(" ") + omml_nary("∑", sub_val=sum_sub, sup_val=sum_sup, e_val=sum_e)

    elif eq_num == 9:
        # v_max = \max_t v(t)
        left = omml_sub(omml_r("v"), omml_r("max", normal=True)) + omml_r(" = ", italic=False)
        max_op = omml_sub(omml_r("max", normal=True), omml_r("t"))
        return left + max_op + omml_r(" ") + omml_r("v") + omml_delim(omml_r("t"))

    elif eq_num == 10:
        # R_residence = (1 / T) * \sum_{t=1}^T I(|| R(t) - C_res ||_2 <= R_res) * 100 (%)
        left = omml_sub(omml_r("R"), omml_r("residence", normal=True)) + omml_r(" = ", italic=False)
        frac = omml_frac(omml_r("1", italic=False), omml_r("T"))
        sum_sub = omml_r("t=1", italic=False)
        sum_sup = omml_r("T")
        norm_inner = omml_r("R", bold=True) + omml_delim(omml_r("t")) + omml_r(" - ", italic=False) + omml_sub(omml_r("C"), omml_r("res", normal=True))
        norm = omml_sub(omml_delim(norm_inner, "‖", "‖"), omml_r("2", italic=False))
        indicator_inner = norm + omml_r(" ≤ ", italic=False) + omml_sub(omml_r("R"), omml_r("res", normal=True))
        sum_e = omml_r("𝕀", normal=True) + omml_delim(indicator_inner) + omml_r(" × 100 (%)", italic=False)
        return left + frac + omml_r(" ") + omml_nary("∑", sub_val=sum_sub, sup_val=sum_sup, e_val=sum_e)

    elif eq_num == 11:
        # D_disp = \max_t || R(t) - C_SOZ ||_2
        left = omml_sub(omml_r("D"), omml_r("disp", normal=True)) + omml_r(" = ", italic=False)
        max_op = omml_sub(omml_r("max", normal=True), omml_r("t"))
        norm_inner = omml_r("R", bold=True) + omml_delim(omml_r("t")) + omml_r(" - ", italic=False) + omml_sub(omml_r("C"), omml_r("SOZ", normal=True))
        norm = omml_sub(omml_delim(norm_inner, "‖", "‖"), omml_r("2", italic=False))
        return left + max_op + omml_r(" ") + norm

    elif eq_num == 12:
        # d_min = \min_t || R(t) - C_res ||_2
        left = omml_sub(omml_r("d"), omml_r("min", normal=True)) + omml_r(" = ", italic=False)
        min_op = omml_sub(omml_r("min", normal=True), omml_r("t"))
        norm_inner = omml_r("R", bold=True) + omml_delim(omml_r("t")) + omml_r(" - ", italic=False) + omml_sub(omml_r("C"), omml_r("res", normal=True))
        norm = omml_sub(omml_delim(norm_inner, "‖", "‖"), omml_r("2", italic=False))
        return left + min_op + omml_r(" ") + norm

    elif eq_num == 13:
        # d_mean = (1 / T) * \sum_{t=1}^T || R(t) - C_res ||_2
        left = omml_sub(omml_r("d"), omml_r("mean", normal=True)) + omml_r(" = ", italic=False)
        frac = omml_frac(omml_r("1", italic=False), omml_r("T"))
        sum_sub = omml_r("t=1", italic=False)
        sum_sup = omml_r("T")
        norm_inner = omml_r("R", bold=True) + omml_delim(omml_r("t")) + omml_r(" - ", italic=False) + omml_sub(omml_r("C"), omml_r("res", normal=True))
        norm = omml_sub(omml_delim(norm_inner, "‖", "‖"), omml_r("2", italic=False))
        return left + frac + omml_r(" ") + omml_nary("∑", sub_val=sum_sub, sup_val=sum_sup, e_val=norm)

    elif eq_num == 14:
        # L_{i,j} = -\log [ exp(sim(z_i, z_j) / \tau) / \sum_{k=1}^{2N} I_{[k \neq i]} exp(sim(z_i, z_k) / \tau) ]
        left = omml_sub(omml_r("ℒ", normal=True), omml_r("i,j")) + omml_r(" = -", italic=False) + omml_r("log", normal=True) + omml_r(" ")
        num = omml_r("exp", normal=True) + omml_delim(omml_frac(omml_r("sim", normal=True) + omml_delim(omml_sub(omml_r("z", bold=True), omml_r("i")) + omml_r(", ") + omml_sub(omml_r("z", bold=True), omml_r("j"))), omml_r("τ", italic=False)))
        sum_sub = omml_r("k=1", italic=False)
        sum_sup = omml_r("2N")
        sum_e = omml_sub(omml_r("𝕀", normal=True), omml_r("[k ≠ i]", italic=False)) + omml_r(" ") + omml_r("exp", normal=True) + omml_delim(omml_frac(omml_r("sim", normal=True) + omml_delim(omml_sub(omml_r("z", bold=True), omml_r("i")) + omml_r(", ") + omml_sub(omml_r("z", bold=True), omml_r("k"))), omml_r("τ", italic=False)))
        den = omml_nary("∑", sub_val=sum_sub, sup_val=sum_sup, e_val=sum_e)
        return left + omml_frac(num, den)

print("OMML definitions generated.")
