# All articles. build.py publishes an article only when its "published" date (Pacific time) has arrived.
# Scheduled runs append new article(...) entries to ARTICLES. See _src/PUBLISHING.md.
from urllib.parse import quote
from html import unescape
import datetime

def _d(iso): return datetime.date.fromisoformat(iso).strftime('%B %-d, %Y')

EV = {  # evidence label keys -> display text (CSS class = key)
    "human-trial": "Human trial",
    "human-obs": "Human observational",
    "animal": "Animal study",
    "cell": "Lab / cells",
    "review": "Review",
}

# Human review: an article shows "Reviewed by" ONLY after the reviewer has actually reviewed it.
# Entries come only from rows Vita marked Approve in the "ÆTAS review log" sheet (see PUBLISHING.md, Human review).
import json as _json, os as _os
REVIEWER = "Vita"
_REVIEWS = _json.load(open(_os.path.join(_os.path.dirname(__file__), "reviews.json"), encoding="utf-8"))
def _review_line(path):
    r = _REVIEWS.get(path)
    if not r: return ""
    by = r.get("by", REVIEWER)
    who = f'{by}, <a href="/editorial-policy/#review">ÆTAS editor</a>' if by == REVIEWER else f'<a href="/editorial-policy/#review">{by}</a>'
    return f' &middot; Reviewed by {who}, {_d(r["date"])}'

def share_box(path, h1):
    url = "https://aetasliveforever.com" + path
    u = quote(url, safe=""); t = quote(unescape(h1), safe="")
    links = [
        ("Facebook", f"https://www.facebook.com/sharer/sharer.php?u={u}"),
        ("LinkedIn", f"https://www.linkedin.com/sharing/share-offsite/?url={u}"),
        ("Pinterest", f"https://pinterest.com/pin/create/button/?url={u}&amp;description={t}"),
        ("X", f"https://twitter.com/intent/tweet?url={u}&amp;text={t}"),
        ("Email", f"mailto:?subject={t}&amp;body={u}"),
    ]
    a = "".join(f'<a href="{h}"{"" if n == "Email" else " target=\"_blank\" rel=\"noopener\""}>{n}</a>' for n, h in links)
    copy = (f'<button type="button" data-url="{url}" onclick="var b=this;navigator.clipboard.writeText(b.dataset.url)'
            f'.then(function(){{b.textContent=\'Link copied\'}},function(){{prompt(\'Copy this link:\',b.dataset.url)}})">Copy link</button>')
    native = (f'<button type="button" class="share-native" hidden data-url="{url}" data-title="{unescape(h1)}" '
              f'onclick="navigator.share({{title:this.dataset.title,url:this.dataset.url}}).catch(function(){{}})">Share</button>'
              f'<script>if(navigator.share)document.currentScript.previousElementSibling.hidden=false</script>')
    return f'<div class="share" aria-label="Share this article"><b>Share:</b> {native}{a}{copy}</div>'

def article(path, hub, hub_name, title, h1, desc, published, intro, quick, evidence, glance, sections, sources, updates=""):
    """
    quick    : 1-3 sentence "Quick answer" (HTML) shown right after the intro.
    evidence : key from EV for the strongest evidence the article rests on.
    glance   : list of (label, value) rows for the "Evidence at a glance" box,
               e.g. [("Best evidence","..."), ("Women included?","..."), ("Bottom line","...")].
    sources  : list of (title, url); primary sources first.
    updates  : optional HTML note of later changes (see corrections in PUBLISHING.md).
    """
    src = "".join(f'<li><a href="{u}" rel="noopener">{t}</a></li>' for t, u in sources)
    rows = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in glance)
    upd = f'<div class="callout"><b>Updates.</b> {updates}</div>' if updates else ""
    body = f'''<section class="hero small"><div class="wrap narrow">
<p class="eyebrow"><a href="{hub}">{hub_name}</a></p>
<h1>{h1}</h1>
<p class="lede">{intro}</p>
<p class="byline">By the <a href="/about/">ÆTAS Research Desk</a>{_review_line(path)} &middot; Checked against sources {_d(published)} &middot; <a href="/editorial-policy/">How we work</a></p>
</div></section>
<section><div class="wrap narrow prose">
<div class="callout quick"><b>Quick answer.</b> {quick}</div>
<div class="evbox"><span class="ev {evidence}">{EV[evidence]}</span> <b>&nbsp;Evidence at a glance</b><dl>{rows}</dl></div>
{sections}
<!--NEWSLETTER-->
{share_box(path, h1)}
{upd}
<h2>Sources</h2><ul class="sources">{src}</ul>
<p class="fine">Wellness education, not medical advice. This article summarizes published research and official sources; it isn&rsquo;t a recommendation for your situation. Talk to your clinician before starting a supplement, device or protocol, especially if you&rsquo;re pregnant, nursing, take medication or manage a health condition.</p>
</div></section>'''
    return {"path": path, "hub": hub, "hub_name": hub_name, "title": title, "h1": h1, "desc": desc, "body": body,
            "article": True, "published": published, "reviewed": published, "evidence": (evidence, EV[evidence])}

ARTICLES = [
article("/supplements/creatine-for-women-over-40/", "/supplements/", "Supplements",
 "Creatine for Women Over 40: What the Research Shows",
 "Creatine for women over 40: what the research actually shows",
 "Does creatine help women over 40 with muscle, bone or brain? What the human trials found, the doses they tested, and the honest bottom line.",
 "2026-10-28",
 "Creatine has gone from gym-bro powder to midlife-women&rsquo;s staple in about two years. The pitch: more muscle, stronger bones, sharper thinking. Here&rsquo;s what the trials in women actually found.",
 "In postmenopausal women, the best trials show creatine adds little or nothing to bone density and only modest extra strength beyond what resistance training already gives. <b>Training is the main event; creatine is, at most, a small add-on.</b> Brain and mood claims rest on small, short studies.",
 "human-trial",
 [("Best evidence", "A 2-year randomized, placebo-controlled trial in 237 postmenopausal women (2023)"),
  ("Women included?", "Yes. The main trials studied women only, mostly after menopause"),
  ("Dose tested", "0.14 g per kg of body weight daily in the 2-year trial, alongside resistance training"),
  ("Bottom line", "No bone-density benefit; small, inconsistent muscle and strength effects; brain findings are early")],
 """<h2>Why creatine for women over 40 is suddenly everywhere</h2>
<p>From the mid-30s on, keeping muscle and bone becomes a priority, and the menopause transition brings an abrupt shift in bone metabolism (see <a href="/news/menopause-physiological-cliff-study/">our news report on a study of a million women</a>). Creatine, a compound your muscles already use for short bursts of energy, has strong evidence for helping athletes train harder. The question is whether that carries over to women in midlife who want to keep their strength and their skeleton.</p>
<p><b>That&rsquo;s a fair question, and it has been tested.</b> Not in mice, but in randomized trials of women.</p>

<h2>What the biggest trial found: creatine and bone density</h2>
<p>The largest and longest study so far followed 237 postmenopausal women, average age 59, for two years. Every woman did the same program: resistance training three days a week and walking six days a week. Half took creatine monohydrate (0.14 g per kilogram of body weight a day); half took a placebo. Neither the women nor the researchers knew who got which.</p>
<p>The results, published in 2023:</p>
<ul>
<li><b>Bone density:</b> no difference. Bone mineral density at the hip (femoral neck), the study&rsquo;s main measure, changed about the same in both groups.</li>
<li><b>Bone shape:</b> the creatine group held on to one measure of hip bone geometry (section modulus) that dropped slightly in the placebo group. That&rsquo;s a hint about bone strength, not proof of fewer fractures.</li>
<li><b>Strength:</b> no difference. Both groups got much stronger on the bench press and squat, because both groups were training.</li>
<li><b>Lean mass:</b> a small edge for creatine only among women who stuck closely to the program; in the full group, it wasn&rsquo;t significant.</li>
<li><b>Walking speed:</b> the creatine group got slightly faster over an 80-meter walk.</li>
</ul>
<p>Notice what the trial design tells you: everyone trained, and everyone got stronger. <a href="/bones/strength-training-bone-density-menopause/">Strength training itself</a> is the better-studied tool for muscle and bone.</p>

<h2>Does creatine build muscle in women after menopause?</h2>
<p>A 2026 review pooled trials that combined supplements with exercise in women across reproductive stages. It included three creatine trials, all in postmenopausal women, with about 300 women analyzed. Its findings:</p>
<ul>
<li>Upper-body strength improved a little more when creatine was added, which the authors attribute largely to creatine.</li>
<li>Muscle mass results were mixed: one short trial found a gain, the two longer ones didn&rsquo;t.</li>
<li><b>Exercise alone was the most reliable intervention.</b> The authors rated the certainty of the evidence as low for muscle and strength and very low for bone.</li>
</ul>

<h2>What about brain fog and mood?</h2>
<p>This is the newest and thinnest part of the evidence. One randomized trial of 36 perimenopausal and menopausal women (average age 50) tested creatine hydrochloride, a different form from the usual monohydrate, for 8 weeks. The middle dose (1,500 mg a day) raised creatine levels in the front of the brain and changed reaction time compared with placebo. The effect on mood swings didn&rsquo;t reach statistical significance.</p>
<p>That&rsquo;s interesting, and it&rsquo;s also 36 women for two months. <b>It&rsquo;s a reason for bigger studies, not a reason to expect clearer thinking.</b></p>

<h2>How much creatine was tested, and in whom</h2>
<table>
<tr><th>Study</th><th>Women</th><th>Dose</th><th>Length</th><th>Main result</th></tr>
<tr><td>Chilibeck et al., 2023</td><td>237 postmenopausal, avg. 59</td><td>0.14 g/kg/day + training</td><td>2 years</td><td>No bone-density benefit</td></tr>
<tr><td>Chen et al., 2026 (review)</td><td>~300 in 3 creatine trials</td><td>Varied</td><td>24&ndash;96 weeks</td><td>Small upper-body strength edge; low certainty</td></tr>
<tr><td>CONCRET-MENOPA, 2025</td><td>36 peri- and postmenopausal, avg. 50</td><td>750&ndash;1,500 mg/day creatine HCl</td><td>8 weeks</td><td>Higher brain creatine; mood not significant</td></tr>
</table>
<p>To put the big trial&rsquo;s dose in context: 0.14 g per kilogram works out to roughly 9.5 g a day for a 150-lb (68 kg) woman. That&rsquo;s the amount a study tested, not a recommendation.</p>

<h2>The honest bottom line</h2>
<ul class="ticks">
<li><b>If your goal is bone:</b> creatine hasn&rsquo;t shown a bone-density benefit in women after menopause. Strength training and a conversation with your clinician about bone screening are the better-supported moves.</li>
<li><b>If your goal is strength:</b> the training does the heavy lifting. Creatine may add a little on top, especially for the upper body.</li>
<li><b>If your goal is your brain:</b> it&rsquo;s too early to say.</li>
</ul>
<p>Creatine is one of the most-studied supplements in sport, but most of that research is in young men. Talk to your clinician before starting it, especially if you have kidney disease, take medication that affects your kidneys, or are pregnant or nursing.</p>
<p>Next up in our evidence checks: <a href="/supplements/magnesium-glycinate-vs-threonate/">magnesium glycinate vs. L-threonate</a> and <a href="/supplements/urolithin-a-evidence/">urolithin A</a>. For the basics, see <a href="/foundations/">Foundations</a>.</p>""",
 [("Chilibeck PD et al. A 2-yr randomized controlled trial on creatine supplementation during exercise for postmenopausal bone health. Med Sci Sports Exerc, 2023", "https://pmc.ncbi.nlm.nih.gov/articles/PMC10487398/"),
  ("Chen et al. Nutritional supplementation combined with exercise for musculoskeletal health in women: a systematic review and meta-analysis. Int J Med Sci, 2026", "https://pmc.ncbi.nlm.nih.gov/articles/PMC13181379/"),
  ("CONCRET-MENOPA: creatine hydrochloride and creatine ethyl ester in perimenopausal and menopausal women, randomized controlled trial. J Am Nutr Assoc, 2025", "https://pubmed.ncbi.nlm.nih.gov/40854087/")]),
article("/news/menopause-physiological-cliff-study/", "/news/", "Latest Research",
 "Menopause Brings Abrupt Body-Wide Changes, Huge Study Finds",
 "Menopause brings abrupt changes in bone, liver and blood fats, huge study finds",
 "A Nature Medicine study of 300 million lab tests from over a million women found a sudden shift at the final period, with hormones changing 12-15 years earlier.",
 "2026-10-28",
 "Menopause is usually described as a slow fade. A study of more than a million women suggests something different: a sharp step change across the body at the final period, with hormone shifts starting more than a decade before.",
 "Researchers analyzed over 300 million routine lab tests from more than a million women in the US and Israel. <b>Many markers, especially bone, liver and blood-fat tests, shifted abruptly around the final menstrual period</b>, while key hormones began changing 12 to 15 years earlier. It&rsquo;s observational, so it shows when things change, not what to do about it.",
 "human-obs",
 [("Study type", "Retrospective analysis of routine lab records (observational)"),
  ("Who", "More than 1 million women in the United States and Israel, 1999&ndash;2024"),
  ("Published", "Nature Medicine, online October 12, 2026"),
  ("Bottom line", "Strong evidence about timing; no evidence yet about which interventions change the curve")],
 """<h2>What the menopause study found</h2>
<p>The team, whose lead author is at the Weizmann Institute of Science in Israel, pooled more than 300 million laboratory tests collected during ordinary medical care. Because the final menstrual period is rarely recorded, past studies have struggled to pin down exactly when changes happen. Working with a dataset this large let them line up women by the timing of their last period and look for patterns.</p>
<ul>
<li><b>An abrupt shift at the final period.</b> In the US data, 52 of the 90 lab tests studied showed a statistically significant, sudden change around menopause.</li>
<li><b>Which systems:</b> the biggest shifts were in bone metabolism, liver tests and how the body handles blood fats. Kidney function and blood chemistry shifted too.</li>
<li><b>Not just aging:</b> men of the same ages didn&rsquo;t show these abrupt changes, so the authors tie them to menopause itself rather than getting older.</li>
</ul>

<h2>Hormones start changing more than a decade earlier</h2>
<p>For women in their late 30s and 40s, this is the part worth noticing. The hormone shifts that lead up to menopause began long before the last period:</p>
<table>
<tr><th>Hormone</th><th>What happened</th><th>When</th></tr>
<tr><td>Anti-M&uuml;llerian hormone (AMH)</td><td>Declined rapidly</td><td>About 15 years before the final period</td></tr>
<tr><td>Follicle-stimulating hormone (FSH)</td><td>Began rising more rapidly</td><td>About 14 years before</td></tr>
<tr><td>Estradiol</td><td>Declined rapidly</td><td>About 12 years before</td></tr>
</table>
<p><b>In other words, the menopause transition is a story that often starts in your late 30s, even if nothing feels different yet.</b></p>

<h2>What about hormone therapy?</h2>
<p>According to the journal&rsquo;s press release, hormone therapy was associated with smaller changes in many measures, particularly bone, liver and kidney markers. The authors themselves say this needs to be confirmed in future studies. Because women weren&rsquo;t randomly assigned to hormone therapy here, the difference could reflect who chooses it, not just what it does.</p>

<h2>What the study can&rsquo;t tell you</h2>
<ul>
<li><b>It&rsquo;s observational.</b> It shows when lab values change, not what causes the change or what prevents it.</li>
<li><b>Menopause status was self-reported</b>, and the data were collected for routine care, not research.</li>
<li><b>&ldquo;Cliff&rdquo; describes lab curves, not how women feel.</b> Experts not involved in the study cautioned that the framing could sound more alarming than the findings, which don&rsquo;t show a dramatic physical or mental decline.</li>
</ul>

<h2>What this means for you</h2>
<p>Nothing here calls for a new supplement or test. What it does support is paying attention before menopause, not after:</p>
<ul class="ticks">
<li>Ask your clinician how they&rsquo;d monitor bone health and cholesterol as you move through your 40s, and what your personal risk factors are.</li>
<li>Keep building muscle and bone with <a href="/bones/strength-training-bone-density-menopause/">strength training</a>, which has the strongest evidence of any habit for both.</li>
<li>If you&rsquo;re weighing hormone therapy, that&rsquo;s a conversation about your own risks and benefits with your doctor, not a decision to make from one observational study.</li>
</ul>
<p>Related: our evidence check on <a href="/supplements/creatine-for-women-over-40/">creatine for women over 40</a>.</p>""",
 [("Pridham G, Hayut Y, Lavi-Shoseyov N, et al. Population-scale reconstruction of menopause dynamics reveals a physiological cliff at the final menstrual period. Nature Medicine, 2026. doi:10.1038/s41591-026-04614-0", "https://www.nature.com/articles/s41591-026-04614-0"),
  ("Nature Portfolio press release on the study, October 13, 2026", "https://www.natureasia.com/en/info/press-releases/detail/9458"),
  ("ScienceAlert: coverage including comments from independent experts, October 13, 2026", "https://sciencealert.com/bones-liver-and-blood-fats-all-shift-abruptly-at-menopause-huge-study-finds")]),
article("/skin/red-light-therapy-skin-over-40/", "/skin/", "Skin",
 "Red Light Therapy for Skin Over 40: What the Evidence Shows",
 "Red light therapy for skin over 40: what the evidence shows",
 "Do LED masks smooth wrinkles after 40? What the studies behind red light therapy found, what FDA clearance means, and how to use a mask safely.",
 "2026-11-01",
 "LED masks are now sold for home use on promises of firmer skin and fewer lines. Before you buy one, here&rsquo;s what the studies behind red light therapy for skin actually show.",
 "Red and near-infrared light may modestly improve fine lines and firmness, but most of the studies behind today&rsquo;s at-home masks are small, short and paid for by the companies that sell them, with no comparison group. <b>FDA clearance means a mask is considered safe and similar to older devices, not that it was proven to work in people.</b>",
 "review",
 [("Best evidence", "Reviews of small clinical studies, plus company-funded studies of specific masks that had no control group"),
  ("Women included?", "Yes. Recent mask studies enrolled mostly or only women aged roughly 41 to 70"),
  ("What was tested", "Red light (about 630&ndash;660 nm), often combined with near-infrared (830 nm and above), for 10&ndash;21 minutes, two to five times a week, over 1&ndash;3 months"),
  ("Bottom line", "Low risk when used as directed, possibly a small benefit, and much less proven than the marketing suggests")],
 """<h2>What red light therapy for skin is supposed to do</h2>
<p>The technique is called photobiomodulation: shining low-power red or near-infrared light on the skin. The leading theory is that the light is absorbed by an enzyme in mitochondria (cytochrome c oxidase), nudging cells to make more energy, and that skin cells called fibroblasts respond by making more collagen.</p>
<p>A 2024 review in the <i>International Journal of Molecular Sciences</i> describes red light as roughly 620 to 700 nanometers and near-infrared as 700 nanometers and up, with longer wavelengths reaching deeper into the skin. The same review notes that <b>there are still no standard recommendations</b> for how much light, how often, or for how long.</p>

<h2>What the studies behind LED masks found</h2>
<p>The studies most often quoted in mask marketing look impressive on paper. Look closely at how they were designed.</p>
<p><b>A luxury-brand mask study (2023).</b> Twenty volunteers aged 45 to 70 used a red-light mask (630 nanometers) for 12 minutes twice a week for three months. Crow&rsquo;s-feet wrinkle depth was reported as 38% lower by the end. But there was no comparison group, participants kept using their own skincare and makeup, and the authors included staff of the cosmetics brand that sells the mask and the chief executive of the company that makes it. The authors themselves list the uncontrolled skincare as a limitation.</p>
<p><b>A multi-wavelength mask study (2026).</b> Thirty-three women aged 41 to 55 used a face mask and a neck mask combining red and near-infrared light (633, 830 and 1,072 nanometers) for 10 minutes, five days a week, for eight weeks; 31 finished. A dermatologist graded fine lines and wrinkles on the face about 6% better, and measured wrinkle depth was about 9% lower. Again, there was no control group, and the study was funded by the device maker, whose innovation manager was the lead author. The authors note that without a control group, expectations may explain part of the result.</p>
<p><b>Why that matters:</b> skin often looks better simply because people in a study are paying attention to it, moisturizing and protecting it from the sun. Without a group using a sham (fake) mask, there&rsquo;s no way to know how much of the change came from the light.</p>

<h2>Are there controlled trials of red light for wrinkles?</h2>
<p>Some exist, and researchers are running more rigorous ones. For example, a team in Brazil published the plan for a randomized, double-blind trial in 108 women aged 45 to 60, all past menopause, comparing two schedules of a red-light (660 nanometer) mask against a sham mask that made the same sound with the light off. That kind of design is what the field needs.</p>
<p>The 2024 review above reports that in the clinical studies it covered, red combined with near-infrared light improved wrinkles, smoothness and firmness. It also points out that treatment schedules varied widely and that protocols haven&rsquo;t been standardized. <b>The honest summary: a plausible, modest effect, from studies that are mostly small and short.</b></p>

<h2>What FDA clearance for an LED mask means</h2>
<p>Many masks advertise that they&rsquo;re &ldquo;FDA cleared.&rdquo; Clearance is not the same as approval. Most at-home LED masks are cleared through the 510(k) process, which asks whether a device is substantially equivalent to one already on the market.</p>
<p>One popular mask cleared in June 2026 for over-the-counter treatment of full-face wrinkles is a good example. Its FDA summary states that clinical performance testing was not needed: clearance rested on comparison with earlier devices and on lab testing for electrical, light and battery safety. Its clearance also covers only lighter to medium skin tones (Fitzpatrick types I to IV).</p>
<p>FDA&rsquo;s own draft guidance for these devices, issued in January 2023, recommends that companies run clinical studies for new devices, ideally with sham or other blinded controls.</p>

<h2>Is red light therapy safe? Eyes come first</h2>
<ul>
<li><b>Your eyes:</b> FDA&rsquo;s draft guidance says light therapy devices can pose a risk of eye damage and recommends that instructions call for safety eyewear when the output requires it. Use the eye protection that comes with the device and never look into the LEDs.</li>
<li><b>Long-term use:</b> the same guidance suggests labels say that the long-term effects of prolonged use are unknown.</li>
<li><b>Cancer:</b> a 2023 systematic review in <i>Aesthetic Surgery Journal</i> looked at 57 papers, including 7 clinical trials, and concluded that current evidence suggests the treatment is safe for skin rejuvenation from a cancer standpoint. Those trials weren&rsquo;t designed to study cancer, so the evidence is limited.</li>
<li><b>Who should check first:</b> FDA&rsquo;s suggested labeling includes warnings about use during pregnancy and over cancerous lesions. If you have a skin condition or a history of skin cancer, ask your clinician first.</li>
</ul>

<h2>Studies at a glance</h2>
<table>
<tr><th>Study</th><th>Who</th><th>Light and schedule</th><th>Control group?</th><th>Reported result</th></tr>
<tr><td>Luxury-brand mask, 2023</td><td>20 volunteers, aged 45&ndash;70</td><td>630 nm; 12 min, twice weekly, 3 months</td><td>No</td><td>Crow&rsquo;s-feet depth about 38% lower</td></tr>
<tr><td>Multi-wavelength mask, 2026</td><td>33 women, aged 41&ndash;55 (31 finished)</td><td>633, 830, 1,072 nm; 10 min, 5 days a week, 8 weeks</td><td>No</td><td>Graded lines about 6% better; wrinkle depth about 9% lower</td></tr>
<tr><td>Brazilian trial plan, 2023</td><td>108 postmenopausal women, aged 45&ndash;60</td><td>660 nm; 21 min sessions, 4 weeks</td><td>Yes (sham mask)</td><td>Protocol only; no results in that paper</td></tr>
</table>

<h2>The honest bottom line</h2>
<ul class="ticks">
<li><b>If you already own a mask:</b> it&rsquo;s low risk when used as directed with eye protection. Expect subtle changes at most, and judge it by photos in the same light over two to three months.</li>
<li><b>If you&rsquo;re deciding whether to buy one:</b> the evidence for a visible difference is weaker than the ads suggest, and &ldquo;FDA cleared&rdquo; doesn&rsquo;t mean proven.</li>
<li><b>If you have darker skin:</b> check the clearance; some masks are cleared only for skin types I to IV.</li>
<li>For in-office options with stronger evidence and more downtime, see our <a href="/procedures/">Procedures</a> section, and browse everything we&rsquo;ve checked in <a href="/skin/">Skin</a>.</li>
</ul>
<p>Related: <a href="/skin/collagen-supplements-skin-evidence/">collagen supplements for skin</a> and <a href="/skin/facial-lymphatic-drainage-evidence/">facial lymphatic drainage</a>.</p>""",
 [("Couturaud V, Le Fur M, Pelletier M, Granotier F. Reverse skin aging signs by red light photobiomodulation. Skin Research and Technology, 2023;29(7):e13391", "https://pmc.ncbi.nlm.nih.gov/articles/PMC10311288/"),
  ("Bradbury E, Langton AK. Multi-Wavelength LED Photobiomodulation Improves Photoaged Skin of the Face, Neck, and D&eacute;collet&eacute;. Cosmetics, 2026;13(5):276", "https://www.mdpi.com/2079-9284/13/5/276"),
  ("Comparison of the effects of 2 frequencies of application of photobiomodulation on facial rejuvenation: controlled, randomized, and double-blind clinical trial (protocol). Medicine, 2023;102(5):e32514", "https://pmc.ncbi.nlm.nih.gov/articles/PMC9902007/"),
  ("U.S. FDA. 510(k) clearance K260715 and summary for an over-the-counter LED light therapy mask, June 3, 2026", "https://www.accessdata.fda.gov/cdrh_docs/pdf26/K260715.pdf"),
  ("U.S. FDA. Photobiomodulation (PBM) Devices: Premarket Notification [510(k)] Submissions. Draft guidance, January 2023", "https://www.fda.gov/media/164417/download"),
  ("Hern&aacute;ndez-Bule ML, Naharro-Rodr&iacute;guez J, Bacci S, Fern&aacute;ndez-Guarino M. Unlocking the Power of Light on the Skin: A Comprehensive Review on Photobiomodulation. International Journal of Molecular Sciences, 2024;25(8):4483", "https://www.mdpi.com/1422-0067/25/8/4483"),
  ("Glass GE. Photobiomodulation: A Systematic Review of the Oncologic Safety of Low-Level Light Therapy for Aesthetic Skin Rejuvenation. Aesthetic Surgery Journal, 2023;43(5):NP357&ndash;NP371", "https://academic.oup.com/asj/article/43/5/NP357/7018419")]),
article("/fitness/vo2-max-women/", "/fitness/", "Fitness",
 "VO2 Max for Women: Why It Matters and How to Raise It",
 "VO2 max for women: why it matters and how to raise it",
 "What VO2 max is, how it changes with age in women, what the mortality research shows, and what trials in women found raises it.",
 "2026-11-04",
 "VO2 max has become the longevity number of the moment, showing up on smartwatches. Here&rsquo;s what it actually measures, why researchers care about it, and what trials in midlife and older women found about raising it.",
 "VO2 max is the most oxygen your body can use during all-out exercise, a measure of cardiorespiratory fitness. In large studies, fitter adults, women included, die at lower rates than less fit adults of the same age and sex. <b>Trials in midlife and older women show regular aerobic exercise raises it, with more exercise bringing bigger gains; interval training raised it too.</b>",
 "human-trial",
 [("Best evidence", "Randomized trials in women: a 6-month trial of 464 postmenopausal women (2007) and a 2026 review of 19 trials in middle-aged and older women. The link to longevity comes from observational studies, such as one of 122,007 adults (2018)"),
  ("Women included?", "Yes. The main trials studied women only; women were about 41% of the large mortality study"),
  ("Protocol tested", "About 72 to 192 minutes a week of moderate exercise for 6 months; interval training in other trials"),
  ("Bottom line", "Higher fitness is linked to a longer life. Moving more raises it, and harder intervals are one more way to do it")],
 """<h2>What is VO2 max?</h2>
<p>VO2 max is the most oxygen your body can take in and use during hard exercise. It&rsquo;s usually written in milliliters of oxygen per kilogram of body weight per minute (mL/kg/min). It reflects how well your heart, lungs, blood and muscles work together.</p>
<p>The most accurate test is done on a treadmill or bike in a lab, wearing a mask that measures your breathing while the effort gets harder until you can&rsquo;t continue. Most other numbers you see, including the one on your watch, are estimates.</p>

<h2>Why VO2 max matters for women: the mortality research</h2>
<p>The study most often cited followed 122,007 adults who took a treadmill test at the Cleveland Clinic between 1991 and 2014. About 41% were women, and the average age was 53. Researchers grouped people by fitness compared with others of the same age and sex, then tracked deaths over a median of 8.4 years. It was published in <i>JAMA Network Open</i> in 2018.</p>
<ul>
<li>People in the lowest fitness group had about 5 times the risk of death of those in the top group (the top 2.3%), after adjusting for other factors.</li>
<li>For comparison, in the same analysis smoking was linked to about 1.4 times the risk, and diabetes about 1.4 times.</li>
<li>In women, the difference between the &ldquo;high&rdquo; and &ldquo;elite&rdquo; fitness groups wasn&rsquo;t statistically significant.</li>
</ul>
<p><b>This is an association, not proof that raising your VO2 max will lengthen your life.</b> Everyone in it was having a treadmill test at a hospital, and fitter people may differ in many other ways that the adjustments can&rsquo;t fully capture.</p>

<h2>How VO2 max changes with age in women</h2>
<p>A US registry of 7,783 lab treadmill tests (3,172 of them in women), collected in 2014 and 2015, set reference values by age. For women, the middle value (50th percentile) was:</p>
<table>
<tr><th>Age</th><th>Middle VO2 max for women (mL/kg/min)</th></tr>
<tr><td>30&ndash;39</td><td>30.2</td></tr>
<tr><td>40&ndash;49</td><td>26.7</td></tr>
<tr><td>50&ndash;59</td><td>23.4</td></tr>
<tr><td>60&ndash;69</td><td>20.0</td></tr>
</table>
<p>Across the adult years, women&rsquo;s values were about 10% lower each decade. These are snapshots of different women at different ages, not the same women followed over time. The menopause years bring other abrupt body changes too (see <a href="/news/menopause-physiological-cliff-study/">our report on a study of a million women</a>).</p>

<h2>How to raise VO2 max: what trials in women found</h2>
<h3>More moderate exercise, more gain</h3>
<p>The DREW trial, published in <i>JAMA</i> in 2007, randomly assigned 464 inactive postmenopausal women in the Dallas area (ages 45 to 75, average 57, all overweight or with obesity and raised blood pressure) to no exercise or one of three exercise amounts for 6 months. The exercise groups worked at a moderate pace, set at about half of each woman&rsquo;s own peak capacity.</p>
<ul>
<li>About 72 minutes a week: fitness up about 4% compared with the control group.</li>
<li>About 136 minutes a week: up about 6%.</li>
<li>About 192 minutes a week: up about 8%.</li>
</ul>
<p><b>Even the smallest amount, well under the official 150 minutes, raised fitness, and more brought more.</b></p>

<h3>Do intervals work better?</h3>
<p>High-intensity interval training (HIIT) alternates hard bursts with easier recovery. A 2026 review in <i>Frontiers in Physiology</i> pooled 19 randomized trials with 646 women aged about 44 to 81, focused on women around and after menopause. In the 8 trials (168 women) that measured VO2 max, HIIT raised it more than the comparison groups, which included no exercise and steady moderate exercise. Trials that measured a closely related number, VO2 peak, didn&rsquo;t show a clear effect. On its own, it did little for everyday physical function such as strength or getting up from a chair.</p>
<p>A small Spanish trial shows what this looks like in practice. It randomized 54 women aged 55 to 85 (average about 68) to hour-long sessions twice a week of either high-intensity interval circuits or steady moderate training, or to no training, for 18 weeks; 41 finished. Compared with the no-training group, estimated VO2 max was about 3.4 mL/kg/min higher with the interval circuits and 1.9 higher with moderate training. The difference between the two training groups wasn&rsquo;t statistically significant, and VO2 max was estimated with an equation, not measured.</p>
<p>In a 2023 review of 29 trials in mostly younger adults (807 people, average age about 34), HIIT came out slightly ahead of steady exercise for fitness, but the authors called the clinical importance of the difference limited.</p>

<h3>What about &ldquo;zone 2&rdquo;?</h3>
<p>&ldquo;Zone 2&rdquo; usually means a steady pace where you can still talk. There&rsquo;s no single agreed definition, and none of the trials described here tested it under that name. The closest evidence here is DREW&rsquo;s moderate pace, which did raise fitness.</p>

<h2>Studies at a glance</h2>
<table>
<tr><th>Study</th><th>Who</th><th>What was tested</th><th>Length</th><th>Main result</th></tr>
<tr><td>Mandsager et al., 2018</td><td>122,007 adults, ~41% women, avg. 53</td><td>Treadmill fitness vs. death (observational)</td><td>Median 8.4 years</td><td>Lowest fitness: ~5x risk vs. top group</td></tr>
<tr><td>DREW (Church et al., 2007)</td><td>464 postmenopausal women, avg. 57</td><td>~72, 136 or 192 min/week moderate exercise</td><td>6 months</td><td>Fitness up ~4%, 6%, 8% vs. control</td></tr>
<tr><td>Cai et al., 2026 (review)</td><td>646 women in 19 trials, ages ~44&ndash;81</td><td>HIIT vs. various controls</td><td>Varied</td><td>VO2 max improved; little effect on function</td></tr>
<tr><td>Ballesta-Garc&iacute;a et al., 2020</td><td>54 women, avg. ~68</td><td>Interval circuits vs. moderate training, 2x/week</td><td>18 weeks</td><td>Both improved; no significant difference</td></tr>
</table>

<h2>How to estimate your VO2 max</h2>
<p>A lab test is the most accurate, but most people rely on a watch. A 2025 review of 13 small studies (273 people, about a third of them women) found that in most of the studies reporting an error figure, watch estimates were within 10% of lab values, while one study found an average error of about 16%, with the watch reading low. Two studies found watches tended to overestimate in less-fit people and underestimate in very fit ones. The review was done by a single author, and none of the studies tested the newest watch models.</p>
<p><b>Use a watch number to watch your own trend, not as a diagnosis.</b> More on device accuracy lives in <a href="/health-trackers/">Health Trackers</a>.</p>

<h2>What this means for you</h2>
<ul class="ticks">
<li><b>Start with the official baseline.</b> US guidelines (HHS) call for 150 to 300 minutes a week of moderate activity, such as brisk walking, or 75 to 150 minutes of vigorous activity, such as running, or a mix, plus muscle-strengthening work on 2 or more days.</li>
<li><b>Any amount counts.</b> In DREW, about 72 minutes a week still moved the needle.</li>
<li><b>Intervals are one more option.</b> Interval sessions raised VO2 max in trials of midlife and older women, but steady exercise worked too.</li>
<li><b>Keep lifting.</b> Cardio doesn&rsquo;t replace <a href="/bones/strength-training-bone-density-menopause/">strength training for bone and muscle</a>.</li>
</ul>
<p>If you have a heart condition, another health condition or an injury, or haven&rsquo;t been active, check with your clinician before starting harder exercise. Find more routines in <a href="/fitness/">Fitness</a> and the basics in <a href="/foundations/">Sleep &amp; Foundations</a>.</p>""",
 [("Mandsager K, Harb S, Cremer P, Phelan D, Nissen SE, Jaber W. Association of Cardiorespiratory Fitness With Long-term Mortality Among Adults Undergoing Exercise Treadmill Testing. JAMA Network Open, 2018;1(6)", "https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2707428"),
  ("Church TS, Earnest CP, Skinner JS, Blair SN. Effects of Different Doses of Physical Activity on Cardiorespiratory Fitness Among Sedentary, Overweight or Obese Postmenopausal Women With Elevated Blood Pressure: A Randomized Controlled Trial. JAMA, 2007;297(19):2081&ndash;2091", "https://jamanetwork.com/journals/jama/fullarticle/1108370"),
  ("Cai L, Guo J, Zhang R, et al. Effects of high intensity interval training (HIIT) on cardiopulmonary fitness and physical function in middle-aged and elderly women: a systematic review and meta-analysis. Frontiers in Physiology, 2026;17", "https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2026.1778052/full"),
  ("Ballesta-Garc&iacute;a I, Mart&iacute;nez-Gonz&aacute;lez-Moro I, Ramos-Campo DJ, Carrasco-Poyatos M. High-Intensity Interval Circuit Training Versus Moderate-Intensity Continuous Training on Cardiorespiratory Fitness in Middle-Aged and Older Women: A Randomized Controlled Trial. IJERPH, 2020;17(5):1805", "https://www.mdpi.com/1660-4601/17/5/1805"),
  ("Guo Z, Li M, Cai J, et al. Effect of High-Intensity Interval Training vs. Moderate-Intensity Continuous Training on Fat Loss and Cardiorespiratory Fitness in the Young and Middle-Aged. IJERPH, 2023;20(6):4741", "https://www.mdpi.com/1660-4601/20/6/4741"),
  ("Kaminsky LA, Arena R, Myers J. Reference Standards for Cardiorespiratory Fitness Measured With Cardiopulmonary Exercise Testing: Data From the FRIEND Registry. Mayo Clinic Proceedings, 2015;90(11):1515&ndash;1523", "https://www.mayoclinicproceedings.org/article/S0025-6196(15)00642-4/pdf"),
  ("&#381;eleznik Me&#382;an L. Accuracy of wearables for determining the maximal oxygen uptake and lactate threshold: a qualitative systematic review. Frontiers in Sports and Active Living, 2025;7:1707991", "https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2025.1707991/full"),
  ("U.S. Department of Health and Human Services. Physical Activity Guidelines for Americans, 2nd edition: Executive Summary", "https://odphp.health.gov/sites/default/files/2019-10/PAG_ExecutiveSummary.pdf"),
  ("CDC. What You Can Do to Meet Physical Activity Recommendations", "https://www.cdc.gov/physical-activity-basics/guidelines/index.html")]),
article("/supplements/urolithin-a-evidence/", "/supplements/", "Supplements",
 "Urolithin A: What the Human Trials Show",
 "Urolithin A: what the human trials actually show",
 "Does urolithin A help muscle and mitochondria? What the human trials found, who was studied, the doses tested and what is still animal-only.",
 "2026-11-06",
 "Urolithin A is sold as a way to renew your mitochondria, the energy factories inside your cells. The most striking results come from worms and mice. Here&rsquo;s what has actually been tested in people, and what it found.",
 "A handful of small, company-sponsored trials, mostly in women, found that urolithin A was well tolerated and shifted some blood and muscle markers linked to mitochondria. <b>On the outcomes you&rsquo;d feel, like walking distance and overall strength, the results are mixed and mostly not better than placebo.</b> The lifespan findings come from worms, not people.",
 "human-trial",
 [("Best evidence", "Two 4-month randomized, placebo-controlled trials (66 and 88 adults, both 2022) and a 2026 meta-analysis of 5 trials (236 people)"),
  ("Women included?", "Yes. Women were about 76% of the older-adult trial and 64% of the midlife trial; the athlete trials studied men only"),
  ("Dose tested", "500 mg or 1,000 mg a day for 4 weeks to 4 months"),
  ("Bottom line", "Well tolerated in short trials; marker changes are real but functional benefits are unproven")],
 """<h2>What is urolithin A?</h2>
<p>Urolithin A is a compound made by gut bacteria from dietary compounds called ellagitannins. Not everyone&rsquo;s gut bacteria make it in the same amounts, which is one reason companies sell it already made.</p>
<p>The interest comes from mitophagy: the cell&rsquo;s way of clearing out worn-out mitochondria. <b>In worms, urolithin A extended lifespan; in rodents, it improved exercise capacity and muscle function.</b> Those are animal results. They explain why people are studying it. They don&rsquo;t tell you what it does in a 45-year-old woman.</p>

<h2>Urolithin A human trials: the first safety study</h2>
<p>The first study in people, published in <i>Nature Metabolism</i> in 2019, tested single doses and then 4 weeks of 500 mg or 1,000 mg a day in healthy, sedentary older adults. Urolithin A reached the blood at every dose and had a favorable safety profile. After 4 weeks, it changed blood levels of acylcarnitines (fat-burning byproducts) and the activity of mitochondrial genes in muscle.</p>
<p>That&rsquo;s a molecular signal, not a measure of strength or energy. The study was sponsored by Amazentis, the company that makes a commercial urolithin A product.</p>

<h2>Does urolithin A improve muscle endurance in older adults?</h2>
<p>A trial in <i>JAMA Network Open</i> (2022) randomized 66 adults aged 65 to 90 in Seattle, average age about 72. <b>Fifty were women (about 76%)</b>, and all were White. Half took 1,000 mg of urolithin A daily for 4 months; half took a placebo. Neither participants nor researchers knew who got which.</p>
<ul>
<li><b>Walking (a main outcome):</b> no significant difference. The urolithin A group walked about 61 meters farther on a 6-minute walk test, but the placebo group improved too, by about 43 meters.</li>
<li><b>Muscle energy production (the other main outcome):</b> no effect on peak energy output in a hand muscle.</li>
<li><b>Muscle endurance:</b> at 2 months, the urolithin A group could do more repeated contractions with a hand muscle and a leg muscle than placebo. By 4 months the difference was no longer significant, because the placebo group had caught up.</li>
<li><b>Blood markers:</b> acylcarnitines and several ceramides (fats linked to metabolic health) fell from baseline in the urolithin A group.</li>
<li><b>Safety:</b> side effects were similar in both groups, with no serious adverse events.</li>
</ul>
<p>Several authors were affiliated with Amazentis, which supplied the capsules.</p>

<h2>What about women in midlife?</h2>
<p>The trial closest to this site&rsquo;s readers, published in <i>Cell Reports Medicine</i> in 2022, randomized 88 sedentary, overweight adults (BMI 25 to 34.9) aged about 40 to 65, average age in the low 50s. <b>Fifty-six were women (about 64%).</b> They took a placebo, 500 mg or 1,000 mg of urolithin A daily for 4 months.</p>
<ul>
<li><b>Main outcome, peak cycling power:</b> no significant difference from placebo.</li>
<li><b>Hamstring strength:</b> rose about 12% on 500 mg and about 10% on 1,000 mg, a significant difference from placebo, whose strength fell. Thigh (quadriceps) strength and grip strength didn&rsquo;t differ.</li>
<li><b>Aerobic fitness:</b> peak oxygen use rose about 10% on 1,000 mg, but the difference from placebo fell just short of significance.</li>
<li><b>Walking:</b> the 1,000 mg group walked about 33 meters farther in 6 minutes, but this wasn&rsquo;t significantly different from placebo.</li>
<li><b>Inflammation:</b> C-reactive protein, a blood marker of inflammation, fell on 1,000 mg.</li>
<li><b>Safety:</b> described as well tolerated; most muscle-related side effects were linked to the biopsy procedure.</li>
</ul>
<p>The lead and senior authors were affiliated with Amazentis, which supplied the product. Lean muscle mass didn&rsquo;t change compared with placebo.</p>

<h2>What does the meta-analysis of urolithin A trials say?</h2>
<p>A 2026 review in <i>Frontiers in Nutrition</i>, by authors who reported no conflicts of interest, pooled the randomized trials of urolithin A and muscle: 5 trials, 236 people. Three of the five studied young male athletes or runners, so the evidence in women rests on the two trials above.</p>
<ul>
<li>Only the 6-minute walk could be combined, from two trials: about 17 meters farther with urolithin A, a difference that wasn&rsquo;t statistically significant. The authors rated certainty as low.</li>
<li>Strength results were mixed: a few measures improved in single trials, while bench press and squat strength didn&rsquo;t differ from placebo.</li>
<li><b>The trials were small and short (4 weeks to 4 months), and long-term safety is unknown.</b> The authors called the findings hypothesis-generating and said larger, longer trials are needed.</li>
</ul>

<h2>Urolithin A doses tested, and in whom</h2>
<table>
<tr><th>Study</th><th>Who</th><th>Dose</th><th>Length</th><th>Main result</th></tr>
<tr><td>Andreux et al., 2019</td><td>Healthy sedentary older adults</td><td>Single doses; then 500 or 1,000 mg/day</td><td>4 weeks</td><td>Safe; mitochondrial markers changed</td></tr>
<tr><td>Liu et al., 2022</td><td>66 adults 65&ndash;90, 76% women</td><td>1,000 mg/day</td><td>4 months</td><td>Walking not better than placebo; early endurance gain</td></tr>
<tr><td>Singh et al., 2022</td><td>88 adults ~40&ndash;65, 64% women</td><td>500 or 1,000 mg/day</td><td>4 months</td><td>Hamstring strength up; main outcome not met</td></tr>
<tr><td>Dao et al., 2026 (review)</td><td>236 people in 5 trials</td><td>500&ndash;1,000 mg/day</td><td>4 weeks&ndash;4 months</td><td>Walking gain not significant; low certainty</td></tr>
</table>
<p>These are the amounts studies tested, not recommendations. Talk to your clinician before starting any supplement.</p>

<h2>Is urolithin A FDA-approved?</h2>
<p>No. In 2018, Amazentis notified the FDA that it considers urolithin A &ldquo;generally recognized as safe&rdquo; (GRAS) as an ingredient in foods such as protein shakes, nutrition bars and yogurts, at up to 500 or 1,000 mg per serving. On December 20, 2018, the FDA replied that it had no questions about that conclusion.</p>
<p><b>A GRAS &ldquo;no questions&rdquo; letter is about safety as a food ingredient. It isn&rsquo;t an approval, and it says nothing about whether urolithin A works.</b></p>

<h2>The honest bottom line</h2>
<ul class="ticks">
<li><b>If your goal is muscle or strength:</b> the trials show scattered gains on some measures and no difference on most. <a href="/bones/strength-training-bone-density-menopause/">Strength training</a> has far stronger evidence.</li>
<li><b>If your goal is energy or fitness:</b> aerobic gains didn&rsquo;t clearly beat placebo. Regular cardio has much stronger evidence for helping you <a href="/fitness/vo2-max-women/">raise VO2 max</a>.</li>
<li><b>If your goal is longevity:</b> the lifespan data are from worms. None of the human trials measured lifespan.</li>
</ul>
<p>All three trials described above involved researchers from the company that makes a commercial urolithin A product, and none lasted longer than 4 months. Talk to your clinician before starting it, especially if you&rsquo;re pregnant, nursing, take medication or manage a health condition.</p>
<p>More evidence checks: <a href="/supplements/creatine-for-women-over-40/">creatine for women over 40</a> and the full <a href="/supplements/">Supplements</a> hub. For the basics, see <a href="/foundations/">Sleep &amp; Foundations</a>.</p>""",
 [("Liu S, et al. Effect of Urolithin A Supplementation on Muscle Endurance and Mitochondrial Health in Older Adults: A Randomized Clinical Trial. JAMA Network Open, 2022;5(1):e2144279", "https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2788244"),
  ("Singh A, et al. Urolithin A improves muscle strength, exercise performance, and biomarkers of mitochondrial health in a randomized trial in middle-aged adults. Cell Reports Medicine, 2022", "https://www.sciencedirect.com/science/article/pii/S2666379122001586"),
  ("Andreux PA, et al. The mitophagy activator urolithin A is safe and induces a molecular signature of improved mitochondrial and cellular health in humans. Nature Metabolism, 2019;1:595&ndash;603", "https://www.nature.com/articles/s42255-019-0073-4"),
  ("Dao T, Nguyen TT, Gariani K, Kim HJ, Ryu D. Effects of Urolithin A supplementation on muscle health outcomes in humans from randomized controlled trials. Frontiers in Nutrition, 2026;13", "https://www.frontiersin.org/journals/nutrition/articles/10.3389/fnut.2026.1834344/full"),
  ("U.S. Food and Drug Administration. GRAS Notice No. 791: Urolithin A", "https://www.hfpappexternal.fda.gov/scripts/fdcc/index.cfm?id=791&set=grasnotices"),
  ("U.S. Food and Drug Administration. Agency Response Letter, GRAS Notice No. GRN 000791", "https://www.fda.gov/media/120300/download")]),
article("/bones/strength-training-bone-density-menopause/", "/bones/", "Bones &amp; Strength",
 "Strength Training for Bone Density Around Menopause",
 "Strength training for bone density around menopause: what the trials show",
 "Can lifting weights protect bone density around menopause? What trials like LIFTMOR found, who was studied, safety, and when to ask about a DEXA scan.",
 "2026-11-10",
 "Bone loss speeds up around menopause, and &ldquo;lift heavy&rdquo; has become the standard advice for midlife women. Here&rsquo;s what the trials of strength training for bone density actually tested, and what they found.",
 "In a randomized trial of 101 postmenopausal women with low bone mass, 8 months of supervised, heavy resistance and impact training raised spine and hip bone density slightly, while a low-intensity home program lost ground. <b>The gains were small, a few percent, and the program was supervised and built up gradually.</b> Trials in perimenopausal women are still small and early.",
 "human-trial",
 [("Best evidence", "LIFTMOR, an 8-month randomized controlled trial of 101 postmenopausal women with low bone mass (2018)"),
  ("Women included?", "Yes. Women only; average age 65 in LIFTMOR and about 53 in a 2026 pilot of 40 peri- and early postmenopausal women"),
  ("Protocol tested", "Twice-weekly, supervised sessions: 5 sets of 5 reps of deadlifts, squats and overhead presses at more than 85% of the most a woman could lift once, plus jumping drops"),
  ("Bottom line", "Supervised, progressive heavy training modestly improved bone density in women with low bone mass; fracture outcomes weren&rsquo;t measured")],
 """<h2>Why bone density changes around menopause</h2>
<p>Bone is living tissue that is constantly broken down and rebuilt. Estrogen helps keep that balance. When estrogen falls, breakdown can outpace rebuilding.</p>
<p>The National Institute on Aging says women may lose bone quickly for several years around menopause, and that the loss slows but continues afterward. The National Institute of Arthritis and Musculoskeletal and Skin Diseases notes that osteoporosis can start a year or two before menopause. According to the NIA, osteoporosis affects about one in five women over 50.</p>
<p><b>Your 40s are when the slope starts, often before anything feels different.</b> Our <a href="/news/menopause-physiological-cliff-study/">report on a study of a million women</a> found bone markers among the measures that shift sharply around the final period.</p>

<h2>What is strength training for bone density?</h2>
<p>Bone responds to load. Exercise that pulls on bone through muscle (lifting) or jolts it on landing (impact) is thought to signal it to rebuild. That&rsquo;s why low-impact and non-weight-bearing activity tends to do little for bone density: a 2025 review in <i>Current Osteoporosis Reports</i> summarized the evidence as showing that walking, cycling and swimming don&rsquo;t produce a positive effect on bone density. They&rsquo;re still good for your heart and mood.</p>
<p>The same review found that only 4 of 63 exercise trials in postmenopausal women in an earlier meta-analysis used high-intensity loads (more than 80% of the most a person can lift once), and that those produced the largest spine gains. <b>For a long time, most trials simply didn&rsquo;t test heavy lifting.</b></p>

<h2>The LIFTMOR trial: heavy lifting in women with low bone mass</h2>
<p>LIFTMOR, published in the <i>Journal of Bone and Mineral Research</i> in 2018, was designed to test whether heavy training was both safe and useful for women whose bones were already thin.</p>
<ul>
<li><b>Who:</b> 101 postmenopausal women, average age 65, all with low bone mass (a T-score below &minus;1.0; a T-score compares your bone density with a healthy young adult&rsquo;s).</li>
<li><b>Design:</b> randomized controlled trial, 8 months.</li>
<li><b>Training group (49 women):</b> two 30-minute supervised sessions a week. Deadlifts, back squats and overhead presses, 5 sets of 5 reps at more than 85% of their one-rep maximum, plus jumping exercises that ended in a landing after dropping from a chin-up bar. Each woman started with a period of technique practice, and the load was increased gradually.</li>
<li><b>Comparison group (52 women):</b> a low-intensity exercise program done at home.</li>
</ul>
<p>What the trial found after 8 months:</p>
<table>
<tr><th>Measure</th><th>Heavy training</th><th>Low-intensity home program</th></tr>
<tr><td>Lumbar spine bone density</td><td>+2.9%</td><td>&minus;1.2%</td></tr>
<tr><td>Femoral neck (hip) bone density</td><td>+0.3%</td><td>&minus;1.9%</td></tr>
<tr><td>Femoral neck cortical thickness</td><td>+13.6%</td><td>+6.3%</td></tr>
<tr><td>Height</td><td>+0.2 cm</td><td>&minus;0.2 cm</td></tr>
</table>
<p>The heavy-training group also did better on every test of physical function, including the timed up-and-go, a reaching test and standing up from a chair five times. Women attended 92% of sessions on average. <b>One adverse event was reported: a minor lower-back spasm.</b></p>
<p>The limits matter. The women were mostly in their 60s, not their 40s. The trial measured bone density and function, not fractures. And every session was supervised.</p>

<h2>Is heavy strength training safe with osteoporosis?</h2>
<p>That was LIFTMOR&rsquo;s first question. The 2025 review reports that about a third of participants had a prior spinal fracture, and the program didn&rsquo;t increase upper-back rounding, cause new or worsening spinal fractures, or worsen scoliosis.</p>
<p>The review is clear about the conditions: training was safe and well tolerated when it was supervised by an exercise physiologist or physiotherapist, tailored to each woman, started with technique practice and progressed gradually. <b>Women with a spinal fracture in the past 12 months were excluded, so there&rsquo;s no evidence for them.</b></p>

<h2>What about strength training in perimenopause?</h2>
<p>Most bone-training trials study women years after menopause. A 2026 pilot from Canada, STOP-EM, published in <i>Bone Reports</i>, looked at the years when loss begins.</p>
<ul>
<li><b>Who:</b> 40 women aged 45 to 60, average age about 53; nearly half were perimenopausal. More than half had normal bone density at the start.</li>
<li><b>Design:</b> randomized, with a waitlist comparison group, 9 months.</li>
<li><b>Program:</b> twice-weekly, 1-hour supervised sessions. A foundation phase, then a building phase, then phases of 5 sets of 5 reps at 80&ndash;85% of one-rep maximum (deadlift, squat, presses, pull-ups or rows) and drop landings from rising platforms.</li>
<li><b>Results:</b> spine bone density, lean mass and leg power were higher than in the waitlist group; hip bone density didn&rsquo;t clearly differ. Balance and estimated aerobic fitness didn&rsquo;t clearly differ either.</li>
</ul>
<p>This was a feasibility study: it tested whether women could do the program, not whether it works. The authors call for a full trial. <b>It&rsquo;s encouraging, and it&rsquo;s 40 women.</b></p>

<h2>Strength training for bone density: the studies at a glance</h2>
<table>
<tr><th>Study</th><th>Women</th><th>Protocol tested</th><th>Length</th><th>Main result</th></tr>
<tr><td>LIFTMOR (Watson et al., 2018)</td><td>101 postmenopausal, avg. 65, low bone mass</td><td>5&times;5 at &gt;85% 1RM + jumping drops, 2&times;/week, supervised</td><td>8 months</td><td>Spine and hip density up vs. low-intensity program</td></tr>
<tr><td>STOP-EM (Whitman et al., 2026)</td><td>40 aged 45&ndash;60, peri- and early postmenopausal</td><td>5&times;5 at 80&ndash;85% 1RM + drop landings, 2&times;/week, supervised</td><td>9 months</td><td>Spine density and lean mass higher; feasibility study</td></tr>
</table>
<p>These are the programs the studies tested, not a prescription. The general guideline is broader: the Physical Activity Guidelines for Americans, as summarized by the CDC, call for muscle-strengthening activity on at least 2 days a week working all major muscle groups, plus 150 minutes of moderate aerobic activity. Adults 65 and older are also advised to include balance activities.</p>

<h2>When should you get a DEXA scan?</h2>
<p>A DEXA (or DXA) scan measures bone density and is the screening test the Task Force refers to. The U.S. Preventive Services Task Force updated its guidance on January 14, 2025:</p>
<ul>
<li><b>Women 65 and older:</b> screening is recommended (grade B).</li>
<li><b>Postmenopausal women under 65 at increased risk:</b> screening is also recommended (grade B). The Task Force describes two steps: a clinician checks for risk factors such as low body weight, a parent who broke a hip, smoking or excess alcohol use, then uses a risk tool such as FRAX to decide whether a scan makes sense.</li>
</ul>
<p>If you&rsquo;re planning to start lifting and wonder where your bones stand, that&rsquo;s a good question to bring to your clinician.</p>

<h2>What this means for you</h2>
<ul class="ticks">
<li><b>Load matters.</b> The trials that moved bone density used heavy, progressive lifting and impact, not light weights or walking alone.</li>
<li><b>Supervision was part of the treatment.</b> Both programs started with technique practice and built up slowly under a trained professional.</li>
<li><b>The gains are modest.</b> A few percent at the spine, smaller at the hip, and no trial here measured fractures.</li>
<li><b>It does more than bone.</b> Strength and physical function improved too, which matters for balance and falls.</li>
</ul>
<p>Check with your clinician before starting, especially if you have osteoporosis, a past fracture, a back or joint injury, a health condition, or haven&rsquo;t been active. More on muscle and midlife: <a href="/supplements/creatine-for-women-over-40/">creatine for women over 40</a>, <a href="/fitness/vo2-max-women/">VO2 max for women</a> and <a href="/meal-plans/protein-needs-women-over-40/">protein needs after 40</a>. See the full <a href="/bones/">Bones &amp; Strength</a> hub.</p>""",
 [("Watson SL, Weeks BK, Weis LJ, Harding AT, Horan SA, Beck BR. High-Intensity Resistance and Impact Training Improves Bone Mineral Density and Physical Function in Postmenopausal Women With Osteopenia and Osteoporosis: The LIFTMOR Randomized Controlled Trial. J Bone Miner Res, 2018;33(2):211&ndash;220", "https://academic.oup.com/jbmr/article/33/2/211/7605709"),
  ("Whitman PW, et al. Preventing muscle and bone loss in peri-menopausal and early post-menopausal females with heavy strength and impact training: the STOP-EM randomised waitlisted controlled feasibility trial. Bone Reports, 2026;30:101931", "https://pmc.ncbi.nlm.nih.gov/articles/PMC13324662/"),
  ("Kumar S, Smith C, Clifton-Bligh RJ, Beck BR, Girgis CM. Exercise for Postmenopausal Bone Health &ndash; Can We Raise the Bar? Curr Osteoporos Rep, 2025;23(1):20", "https://pmc.ncbi.nlm.nih.gov/articles/PMC11985624/"),
  ("U.S. Preventive Services Task Force. Osteoporosis to Prevent Fractures: Screening (final recommendation, January 14, 2025)", "https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/osteoporosis-screening"),
  ("National Institute on Aging. Osteoporosis", "https://www.nia.nih.gov/health/osteoporosis/osteoporosis"),
  ("National Institute of Arthritis and Musculoskeletal and Skin Diseases. Osteoporosis", "https://www.niams.nih.gov/health-topics/osteoporosis"),
  ("Centers for Disease Control and Prevention. Adult Activity: An Overview", "https://www.cdc.gov/physical-activity-basics/guidelines/adults.html"),
  ("Centers for Disease Control and Prevention. Older Adult Activity: An Overview", "https://www.cdc.gov/physical-activity-basics/guidelines/older-adults.html")]),
article("/hair/female-hair-loss-causes/", "/hair/", "Hair",
 "Hair Loss in Women: Causes and How to Tell Them Apart",
 "Hair loss in women: the most common causes and how to tell them apart",
 "Thinning, shedding or bald patches? The main causes of hair loss in women, how each one looks, and what to ask a dermatologist to check.",
 "2026-11-11",
 "Finding more hair in the drain, or a part that looks wider than it used to, is unsettling. &ldquo;Hair loss&rdquo; covers several different conditions, and they look, behave and are treated differently. Here&rsquo;s how dermatology sources tell them apart.",
 "The most common causes of hair loss in women are female pattern hair loss (gradual thinning over the top of the head), telogen effluvium (sudden, all-over shedding a few months after a stressor), alopecia areata (round bald patches), traction alopecia (from tight hairstyles) and the scarring alopecias. <b>The pattern of loss, how fast it came on and whether the scalp itches or hurts are the biggest clues, and a board-certified dermatologist can confirm which one it is.</b>",
 "review",
 [("Best evidence", "Clinical reviews and official health sources (NIH, MedlinePlus), plus a 2022 meta-analysis of 36 observational studies in 10,029 women on iron and hair loss"),
  ("Women included?", "Yes. Most sources describe women specifically; the iron meta-analysis included only women"),
  ("Dose or protocol tested", "None. This is an overview of causes and diagnosis, not a treatment study"),
  ("Bottom line", "Different kinds of hair loss look different. Some are temporary, some are treatable, and the scarring types are worth catching early")],
 """<h2>Is some shedding normal?</h2>
<p>Yes. Hair grows in cycles: a long growing phase, then a resting phase, after which the hair falls out and a new one starts. MedlinePlus, the National Library of Medicine&rsquo;s health site, puts normal shedding at roughly 50 to 200 hairs a day.</p>
<p>It&rsquo;s worth a closer look when shedding is clearly above your usual, your part or ponytail looks thinner, or bare patches appear. <b>The shape of the loss is the first clue to the cause.</b></p>

<h2>Female pattern hair loss: gradual thinning on top</h2>
<p>Female pattern hair loss (also called androgenetic alopecia) is the most common type. Follicles on the top of the head slowly shrink, so each new hair grows back finer and shorter.</p>
<ul>
<li><b>How it looks:</b> thinning over the crown and top of the head, often with a part that widens toward the front in a &ldquo;Christmas tree&rdquo; shape. The front hairline is usually kept. Complete baldness is rare.</li>
<li><b>How common:</b> a 2018 review in the <i>International Journal of Women&rsquo;s Dermatology</i> reports that about 12% of women show it by age 29, 25% by 49 and 41% by 69.</li>
</ul>
<p>A 2022 review in <i>Clinical and Experimental Dermatology</i> notes it commonly shows up around menopause and that most women with it have normal androgen (male-type hormone) levels. It says blood tests usually aren&rsquo;t needed unless the loss is severe or sudden, or there are signs of high androgens, such as facial hair, acne or irregular periods.</p>
<p>According to MedlinePlus, topical minoxidil is the only medicine the FDA has approved for female pattern hair loss. More on how it changes in midlife: <a href="/hair/hair-thinning-perimenopause/">hair thinning in perimenopause</a> and <a href="/hair/minoxidil-for-women/">minoxidil for women</a>.</p>

<h2>Telogen effluvium: sudden shedding after a stressor</h2>
<p>Telogen effluvium is a shift of many growing hairs into the resting phase at once. Months later, they shed together.</p>
<ul>
<li><b>How it looks:</b> diffuse shedding all over the scalp, often noticed in the shower or on the pillow. There&rsquo;s no bald patch.</li>
<li><b>Timing:</b> a StatPearls review (NIH&rsquo;s National Library of Medicine) says the trigger usually happens about 3 months before shedding starts, with a range of 1 to 6 months. That delay is why many people don&rsquo;t connect the two.</li>
<li><b>Common triggers:</b> high fever or a severe infection, childbirth, major surgery, severe emotional stress, crash diets or low protein intake, iron deficiency, an underactive thyroid, and stopping an estrogen-containing medication. MedlinePlus also lists some medicines, including retinoids and beta-blockers.</li>
</ul>
<p>MedlinePlus says this shedding can involve half to three-quarters of scalp hair. StatPearls describes the acute form as lasting under 6 months, with full recovery taking several months to a year; a chronic form can last longer. <b>Telogen effluvium is usually temporary once the trigger has passed.</b> See our guide to <a href="/hair/telogen-effluvium/">telogen effluvium</a>.</p>

<h2>Alopecia areata: round bald patches</h2>
<p>Alopecia areata is an autoimmune condition: the immune system attacks hair follicles and stops growth.</p>
<ul>
<li><b>How it looks:</b> small, round, coin-sized bare patches, most often on the scalp, sometimes on the eyebrows or elsewhere. Some people also get small pits in their nails.</li>
<li><b>How common:</b> MedlinePlus Genetics estimates 1 in every 500 to 1,000 people in the U.S., affecting men and women equally.</li>
<li><b>Outlook:</b> the follicles aren&rsquo;t permanently damaged, so hair can regrow. The National Institute of Arthritis and Musculoskeletal and Skin Diseases (NIAMS) says that for many people it grows back without treatment, though it can fall out again.</li>
</ul>
<p>People with alopecia areata have a higher risk of other autoimmune conditions, including thyroid disease and vitiligo. NIAMS notes that JAK inhibitors are approved for adults with severe disease.</p>

<h2>Traction alopecia: loss from tight hairstyles</h2>
<p>Traction alopecia comes from long-term pulling on the follicles: tight ponytails, buns, braids, cornrows, weaves and extensions. Women of African descent with tightly curled hair are most often affected.</p>
<p>It usually shows up as thinning along the front and sides of the hairline, sometimes with a fringe of fine, short hairs left at the edge. <b>Early on it&rsquo;s reversible: switching to looser styles can lead to full regrowth. Years of tension can scar the follicles for good.</b></p>

<h2>Scarring alopecias: the hair loss not to wait on</h2>
<p>In scarring (cicatricial) alopecias, inflammation destroys follicles and replaces them with scar tissue, so hair in those spots can&rsquo;t regrow. Treatment aims to stop it spreading. Two matter most for women in midlife:</p>
<ul>
<li><b>Frontal fibrosing alopecia:</b> a slowly receding band along the front and sides of the hairline. A StatPearls review says it mainly affects postmenopausal women, typically around 60, and the 2022 menopause review links it to the perimenopausal years. Eyebrow loss is common; it was seen in 81% of patients in the original case series and can come before the hairline changes.</li>
<li><b>Central centrifugal cicatricial alopecia (CCCA):</b> hair loss that starts at the crown and spreads outward. It&rsquo;s the most common scarring alopecia in women of African descent, with an average age of onset of 36, according to StatPearls. Burning, tenderness or itching in the area can occur.</li>
</ul>
<p><b>Both sources stress that catching scarring alopecia early is what helps limit permanent loss.</b></p>

<h2>Hair loss in women: how the causes compare</h2>
<table>
<tr><th>Cause</th><th>Where</th><th>Onset</th><th>Scalp symptoms</th><th>Can hair regrow?</th></tr>
<tr><td>Female pattern hair loss</td><td>Top and crown; front hairline kept</td><td>Gradual, over years</td><td>Usually none</td><td>Progressive; treatment can slow it</td></tr>
<tr><td>Telogen effluvium</td><td>All over</td><td>Sudden, 1&ndash;6 months after a trigger</td><td>Usually none</td><td>Usually yes</td></tr>
<tr><td>Alopecia areata</td><td>Round patches; eyebrows possible</td><td>Over weeks</td><td>Usually none; nail pits possible</td><td>Often yes; may recur</td></tr>
<tr><td>Traction alopecia</td><td>Front and sides of hairline</td><td>Gradual</td><td>Sometimes redness at the hairline</td><td>Yes if caught early; can become permanent</td></tr>
<tr><td>Scarring alopecias (FFA, CCCA)</td><td>Hairline band (FFA) or crown (CCCA)</td><td>Gradual</td><td>CCCA: sometimes burning, itching or tenderness</td><td>No in scarred areas</td></tr>
</table>
<p>More than one can happen at once, such as shedding after an illness on top of pattern thinning.</p>

<h2>What medical causes of hair loss should be ruled out?</h2>
<p>Several health issues can cause or worsen shedding. These are the ones the sources name:</p>
<ul>
<li><b>Thyroid disease.</b> Both MedlinePlus and StatPearls list it; StatPearls suggests a TSH blood test when there are symptoms of an underactive thyroid, such as tiredness, weight gain or feeling cold.</li>
<li><b>Low iron.</b> A 2022 meta-analysis in <i>Skin Appendage Disorders</i> pooled 36 observational studies of 10,029 women and found that women with non-scarring hair loss had lower ferritin (stored iron) on average than women without it. Iron-deficiency anemia wasn&rsquo;t more common. These studies show a link, not that iron causes or fixes the loss. StatPearls adds that a normal ferritin doesn&rsquo;t fully rule out iron deficiency. More: <a href="/hair/iron-ferritin-hair-loss/">iron, ferritin and hair loss</a>.</li>
<li><b>Hormones.</b> Signs of high androgens (facial hair, acne, irregular periods) point toward conditions like PCOS. Childbirth, starting or stopping estrogen-containing birth control, and menopause can all affect shedding.</li>
<li><b>Vitamin D.</b> The 2018 review cites a single study linking low vitamin D with shedding and pattern thinning; the evidence is thin.</li>
<li><b>Other conditions.</b> MedlinePlus also lists lupus and scalp infections.</li>
</ul>
<p>Don&rsquo;t stop or change any medication because of hair loss; ask the clinician who prescribed it.</p>

<h2>When to see a dermatologist about hair loss</h2>
<p>MedlinePlus advises contacting a provider if you notice:</p>
<ul class="ticks">
<li>Hair loss in an unusual pattern, or loss that&rsquo;s fast</li>
<li>Pain, itching, redness or scaling on the scalp</li>
<li>Acne, new facial hair or changes in your periods along with the hair loss</li>
<li>Bald patches, including on the eyebrows</li>
<li>Tiredness, weight gain, muscle weakness or feeling cold</li>
</ul>
<p>A dermatologist usually starts with your history and a close look at the scalp. They may do a gentle pull test, order blood tests, or, less often, take a small biopsy. <b>Any receding hairline, eyebrow loss or scalp symptoms are reasons not to wait.</b></p>

<h2>The honest bottom line</h2>
<p>Most hair loss in women is gradual pattern thinning or temporary shedding after a stressor. Patches, a receding hairline, eyebrow loss, or an itchy or sore scalp point to other causes worth a prompt visit.</p>
<p>Questions to bring to a board-certified dermatologist:</p>
<ul>
<li>Which type of hair loss is this, and do I need a biopsy to be sure?</li>
<li>Could something in the last six months have triggered shedding?</li>
<li>Which blood tests make sense for me, such as thyroid or iron studies?</li>
<li>Is there any sign of scarring?</li>
<li>Which treatments have FDA approval or trial evidence for my type, and what are their side effects?</li>
</ul>
<p>Explore the full <a href="/hair/">Hair</a> hub and our <a href="/news/menopause-physiological-cliff-study/">report on how the body shifts around menopause</a>.</p>""",
 [("Fabbrocini G, Cantelli M, Masar&agrave; A, Annunziata MC, Marasca C, Cacciapuoti S. Female pattern hair loss: A clinical, pathophysiologic, and therapeutic review. Int J Womens Dermatol, 2018;4(4):203&ndash;211", "https://www.sciencedirect.com/science/article/pii/S2352647518300224"),
  ("Kamp E, Ashraf M, Musbahi E, DeGiovanni C. Menopause, skin and common dermatoses. Part 1: hair disorders. Clin Exp Dermatol, 2022;47(12):2110&ndash;2116", "https://academic.oup.com/ced/article/47/12/2110/6966259"),
  ("Treister-Goltzman Y, Yarza S, Peleg R. Iron Deficiency and Nonscarring Alopecia in Women: Systematic Review and Meta-Analysis. Skin Appendage Disord, 2022;8(2):83&ndash;92", "https://karger.com/sad/article/8/2/83/826740/Iron-Deficiency-and-Nonscarring-Alopecia-in-Women"),
  ("Hughes EC, Syed HA, Saleh D. Telogen Effluvium. StatPearls, NCBI Bookshelf (updated May 1, 2024)", "https://www.ncbi.nlm.nih.gov/sites/books/NBK430848/"),
  ("Syed HA, Kaliyadan F. Traction Alopecia. StatPearls, NCBI Bookshelf (updated May 4, 2025)", "https://www.ncbi.nlm.nih.gov/sites/books/NBK470434/"),
  ("Syed HA, Idoudi S. Frontal Fibrosing Alopecia. StatPearls, NCBI Bookshelf (updated June 7, 2024)", "https://www.ncbi.nlm.nih.gov/sites/books/NBK519001/"),
  ("Gabros S, Sathe NC, Masood S. Central Centrifugal Cicatricial Alopecia. StatPearls, NCBI Bookshelf (updated March 13, 2024)", "https://www.ncbi.nlm.nih.gov/sites/books/NBK559187/"),
  ("National Institute of Arthritis and Musculoskeletal and Skin Diseases. Alopecia Areata: Diagnosis, Treatment, and Steps to Take", "https://www.niams.nih.gov/health-topics/alopecia-areata/diagnosis-treatment-and-steps-to-take"),
  ("MedlinePlus Genetics. Alopecia areata", "https://medlineplus.gov/genetics/condition/alopecia-areata/"),
  ("MedlinePlus Medical Encyclopedia. Hair loss", "https://medlineplus.gov/ency/article/003246.htm"),
  ("MedlinePlus Medical Encyclopedia. Female pattern baldness", "https://medlineplus.gov/ency/article/001173.htm")]),

article("/hair/rosemary-oil-hair-growth/", "/hair/", "Hair",
 "Rosemary Oil for Hair Growth: What the Trial Found",
 "Rosemary oil for hair growth: what the one trial really found",
 "Does rosemary oil regrow hair? The one randomized trial studied men, not women. What it found, what's missing, and what to know about skin reactions.",
 "2026-11-13",
 "Rosemary oil is one of the most shared hair-growth tips online, usually with a claim that it works as well as minoxidil. That claim traces back to a single trial. Here&rsquo;s what that trial did, who was in it, and what it can and can&rsquo;t tell a woman with thinning hair.",
 "One randomized trial from 2015 found that men with pattern hair loss who used rosemary oil for 6 months gained a similar amount of hair as men using 2% minoxidil. <b>There is no randomized trial of rosemary oil alone in women, and the one trial had no placebo group, so it can&rsquo;t show how much rosemary itself did.</b>",
 "human-trial",
 [("Best evidence", "One randomized, single-blind trial of 100 people with androgenetic alopecia (2015), comparing rosemary oil with 2% minoxidil"),
  ("Women included?", "No. The trial enrolled men aged 18&ndash;49. The only study in women tested a multi-ingredient serum, with no control group, and was funded by its maker"),
  ("Protocol tested", "Topical rosemary oil vs. topical 2% minoxidil for 6 months"),
  ("Bottom line", "An early, men-only result with no placebo comparison. Not enough to know whether rosemary oil helps women&rsquo;s hair loss")],
 """<h2>Where the &ldquo;rosemary oil works like minoxidil&rdquo; claim comes from</h2>
<p>Almost every rosemary-for-hair post points to one paper: a randomized trial by Panahi and colleagues, published in the dermatology journal <i>SKINmed</i> in 2015. It compared rosemary oil with minoxidil, the drug in many over-the-counter hair regrowth products.</p>
<p>Dermatology reviews from 2024 and 2025 point to this same trial as the human evidence for rosemary oil in pattern hair loss. <b>So the claim rests on one study.</b></p>

<h2>What the rosemary oil trial actually tested</h2>
<ul>
<li><b>Who:</b> 100 people with androgenetic alopecia (pattern hair loss). A 2024 review describes them as men aged 18 to 49. No women were included.</li>
<li><b>Design:</b> randomized and single-blind. 50 people used rosemary oil and 50 used 2% minoxidil on the scalp.</li>
<li><b>How long:</b> 6 months, with check-ins at 3 and 6 months.</li>
<li><b>What was measured:</b> hair counts from standardized close-up scalp photos, plus dryness, greasiness, dandruff and itching.</li>
</ul>

<h2>What did the rosemary oil trial find?</h2>
<p>At 3 months, neither group had a meaningful change in hair count. At 6 months, both groups had significantly more hair than at the start, and <b>the two groups didn&rsquo;t differ from each other.</b></p>
<p>Dryness, greasiness and dandruff didn&rsquo;t change in either group. Scalp itching rose in both groups compared with the start, and it was more common with minoxidil than with rosemary oil at both check-ins.</p>
<p>The authors concluded that rosemary oil showed evidence of benefit for pattern hair loss. That&rsquo;s the source of the &ldquo;as good as minoxidil&rdquo; headline.</p>

<h2>Why one trial isn&rsquo;t enough</h2>
<p>The result is interesting, but it has real limits:</p>
<ul>
<li><b>No placebo group.</b> Both groups got an active treatment. Without a group using a plain oil or nothing, there&rsquo;s no way to tell how much of the gain came from rosemary itself.</li>
<li><b>Only men.</b> Pattern hair loss in women tends to look and behave differently from men&rsquo;s, so results in men aged 18 to 49 may not carry over.</li>
<li><b>One small study, never repeated.</b> A 2025 review in the <i>International Journal of Trichology</i> notes it&rsquo;s a single study and doesn&rsquo;t call its results conclusive.</li>
<li><b>&ldquo;No difference&rdquo; isn&rsquo;t the same as &ldquo;equal.&rdquo;</b> A trial of 100 people can miss a real gap between two treatments.</li>
</ul>
<p>A 2024 review in <i>Clinical, Cosmetic and Investigational Dermatology</i> that leaned positive on rosemary still concluded that more studies are needed before its benefits can be confirmed.</p>

<h2>Is there any rosemary oil study in women?</h2>
<p>Not of rosemary oil on its own. The closest is a 2025 study in <i>Cureus</i> of a hair serum that contained rosemary oil among about ten ingredients, including caffeine, biotin, tea tree oil and several branded plant extracts.</p>
<ul>
<li><b>Who:</b> 32 healthy women aged 20 to 45 (average about 38) with self-reported thinning and some grey hair; 30 finished.</li>
<li><b>Design:</b> open-label and single-arm. Everyone used the serum, there was no comparison group, and participants knew what they were using.</li>
<li><b>How long:</b> 120 days, once a day.</li>
<li><b>Found:</b> the authors reported gains in hair growth rate, density and thickness, and less shedding.</li>
<li><b>Funding:</b> the study was paid for by the company that makes the serum, and one author works for and holds stock in that company.</li>
</ul>
<p><b>With a mix of ingredients and no control group, this study can&rsquo;t say whether rosemary did anything.</b></p>

<h2>Lab and animal studies: promising, but not proof</h2>
<p>Much of the interest in rosemary comes from lab and mouse work, not people. The 2024 review describes experiments in which rosemary leaf <i>extract</i> (a different product from the essential oil sold for hair) blocked 5-alpha-reductase, the enzyme that makes DHT, a hormone involved in pattern hair loss. It names a compound called 12-methoxycarnosic acid as the most active.</p>
<p>That&rsquo;s a reasonable idea to test, but enzyme results in a dish and hair regrowth in mice don&rsquo;t tell us what a scalp oil does for a woman. <b>Treat this as a reason for better trials, not as evidence for people.</b></p>

<h2>Rosemary oil safety: irritation and skin allergy</h2>
<p>&ldquo;Natural&rdquo; doesn&rsquo;t mean gentle on skin.</p>
<ul>
<li>In the 2015 trial, scalp itching increased from the start in the rosemary group, though less than with minoxidil.</li>
<li>In the 2025 women&rsquo;s serum study, 2 of the participants reported scalp irritation on the first day.</li>
<li>In a 2025 safety opinion on rosemary oil as an animal feed additive, the European Food Safety Authority&rsquo;s scientific panel said the oil should be considered an irritant to skin and eyes and a skin sensitiser, meaning it can trigger an allergic skin reaction in some people.</li>
</ul>
<p>If your scalp gets red, itchy, burning or flaky after using any product, stop and check with a dermatologist.</p>

<h2>How rosemary oil compares with the evidence for other options</h2>
<table>
<tr><th>Study</th><th>Who</th><th>Design</th><th>Length</th><th>Result</th></tr>
<tr><td>Panahi et al., <i>SKINmed</i> 2015</td><td>100 men, 18&ndash;49, pattern hair loss</td><td>Randomized, single-blind; rosemary oil vs. 2% minoxidil; no placebo</td><td>6 months</td><td>Hair counts rose in both groups at 6 months; no difference between groups</td></tr>
<tr><td>Patel et al., <i>Cureus</i> 2025</td><td>30 women, 20&ndash;45</td><td>Open-label, single-arm; multi-ingredient serum; maker-funded</td><td>120 days</td><td>Authors reported gains; can&rsquo;t isolate rosemary</td></tr>
<tr><td>Lab and mouse studies (reviewed 2024)</td><td>Cells and mice</td><td>Rosemary leaf extract, not oil</td><td>&mdash;</td><td>Blocked the DHT-making enzyme; not tested this way in people</td></tr>
</table>

<h2>What this means for you</h2>
<p>Rosemary oil has one encouraging, small trial behind it, and that trial studied men and lacked a placebo group. <b>For women, there&rsquo;s no good evidence yet either way.</b> It&rsquo;s also not a substitute for finding out why your hair is thinning, since some causes, like low iron, thyroid problems or scarring hair loss, need their own care. Start with our guide to <a href="/hair/female-hair-loss-causes/">the causes of hair loss in women</a> and our <a href="/news/menopause-physiological-cliff-study/">report on how the body shifts around menopause</a>.</p>
<p>Questions to bring to a board-certified dermatologist:</p>
<ul>
<li>What type of hair loss do I have, and what&rsquo;s likely causing it?</li>
<li>Which treatments have FDA approval or trial evidence for my type? (See <a href="/hair/minoxidil-for-women/">minoxidil for women</a>.)</li>
<li>Could a scalp oil or serum irritate my skin or interact with anything I already use?</li>
<li>How long should I give any treatment before judging whether it&rsquo;s working?</li>
</ul>
<p>More evidence checks on popular natural remedies are coming in our <a href="/hair/">Hair</a> hub, including <a href="/hair/pumpkin-seed-oil-hair/">pumpkin seed oil</a> and <a href="/hair/peppermint-oil-hair/">peppermint oil</a>.</p>""",
 [("Panahi Y, et al. Rosemary oil vs minoxidil 2% for the treatment of androgenetic alopecia: a randomized comparative trial. SKINmed, 2015;13(1):15&ndash;21", "https://pubmed.ncbi.nlm.nih.gov/25842469/"),
  ("Bin Rubaian NF, Alzamami HFA, Amir BA. An Overview of Commonly Used Natural Alternatives for the Treatment of Androgenetic Alopecia, with Special Emphasis on Rosemary Oil. Clin Cosmet Investig Dermatol, 2024;17:2495&ndash;2503", "https://pmc.ncbi.nlm.nih.gov/articles/PMC11549889/"),
  ("Bikash C. Topical Alternatives for Hair Loss: Beyond the Conventional. Int J Trichology, 2025;17(1):13&ndash;19", "https://pmc.ncbi.nlm.nih.gov/articles/PMC12251978/"),
  ("Patel M, Tuli N, Patel N, Merja A. A Clinical Evaluation of the Safety, Efficacy, and Tolerability of a Rosemary Redensyl Hair Growth Serum in Healthy Female Subjects. Cureus, 2025;17(1):e77066", "https://pmc.ncbi.nlm.nih.gov/articles/PMC11800316/"),
  ("EFSA Panel on Additives and Products or Substances used in Animal Feed (FEEDAP). Safety and efficacy of a feed additive consisting of an essential oil derived from Salvia rosmarinus (rosemary oil). EFSA Journal, 2025;23(10):e9685", "https://pmc.ncbi.nlm.nih.gov/articles/PMC12531593/")]),


article("/supplements/nmn-nad-supplements-women/", "/supplements/", "Supplements",
 "NMN and NAD+ Supplements: What Human Trials Show",
 "NMN and NAD+ supplements: what human trials show",
 "Do NMN and NR supplements work? What human trials found, including one in postmenopausal women, where they fell short, and where the FDA stands.",
 "2026-11-13",
 "NMN and NR are sold as ways to raise NAD+, a molecule your cells need to make energy. The excitement comes largely from mice. Here&rsquo;s what has happened when people, including women after menopause, actually took them.",
 "Human trials show NMN and NR reliably raise NAD+ levels in blood, but <b>measurable health benefits have been small, inconsistent and mostly short-term.</b> The best-known trial in women, 25 postmenopausal women with prediabetes, found better insulin sensitivity in muscle after 10 weeks of NMN, with no change in body fat, blood pressure, blood sugar or cholesterol.",
 "human-trial",
 [("Best evidence", "Small randomized, placebo-controlled trials, usually 40 people or fewer and a few weeks to 3 months long; the key women-only trial had 25 participants (2021)"),
  ("Women included?", "Some. One randomized trial enrolled only postmenopausal women; several others studied only men"),
  ("Dose tested", "Most NMN trials tested 250 to 1,200 mg a day; most NR trials 1,000 to 2,000 mg a day"),
  ("Bottom line", "They raise NAD+ in blood. Whether that improves health in people is still unproven")],
 """<h2>What are NMN, NR and NAD+?</h2>
<p>NAD+ (nicotinamide adenine dinucleotide) is a helper molecule cells need to turn food into energy. NMN (nicotinamide mononucleotide) and NR (nicotinamide riboside) are building blocks, or precursors, the body can convert into NAD+.</p>
<p>In mice, raising NAD+ improved many measures of aging. A 2023 review of the human trials in the <i>Journals of Gerontology</i> points out that mouse studies often used higher doses for longer than human trials, and that <b>many human trials haven&rsquo;t shown clinically meaningful benefits.</b></p>

<h2>The NMN trial in postmenopausal women</h2>
<p>The trial most relevant to ÆTAS readers was published in <i>Science</i> in 2021 by a team at Washington University in St. Louis, with funding in part from two NIH institutes.</p>
<ul>
<li><b>Who:</b> 25 postmenopausal women aged roughly 55 to 75 who were overweight or had obesity and had prediabetes.</li>
<li><b>Design:</b> randomized, double-blind and placebo-controlled. 13 took NMN and 12 took a placebo.</li>
<li><b>Dose and length:</b> 250 mg of NMN a day for 10 weeks.</li>
<li><b>What was measured:</b> insulin sensitivity using a gold-standard test (a &ldquo;clamp&rdquo; study), plus body composition, blood pressure, blood fats and muscle samples.</li>
</ul>
<p><b>What improved:</b> muscle&rsquo;s ability to take up sugar in response to insulin rose about 25% with NMN, according to NIH&rsquo;s summary of the study, with no such change on placebo. NAD+ rose in blood cells.</p>
<p><b>What didn&rsquo;t change:</b> body fat, blood pressure, blood sugar and insulin levels, cholesterol and other blood fats, and the liver&rsquo;s response to insulin. NAD+ in muscle itself didn&rsquo;t rise.</p>
<p>The study&rsquo;s senior author told NIH it was too early to make clinical recommendations from these results. <b>It&rsquo;s one small, 10-week trial with a lab measure as its main result, not evidence that NMN lowers anyone&rsquo;s diabetes risk.</b></p>

<h2>What other NMN trials found</h2>
<p>The 2023 review summarizes about a dozen NMN trials. Most were small and short. A few examples:</p>
<table>
<tr><th>Trial</th><th>Who</th><th>NMN tested</th><th>Length</th><th>Result</th></tr>
<tr><td>Yoshino (2021)</td><td>25 postmenopausal women with prediabetes</td><td>250 mg/day</td><td>10 weeks</td><td>Muscle insulin sensitivity up; body fat, blood pressure, glucose, lipids unchanged</td></tr>
<tr><td>Igarashi</td><td>42 men aged 65+</td><td>250 mg/day</td><td>12 weeks</td><td>Walking speed and grip strength improved; muscle mass unchanged</td></tr>
<tr><td>Yi</td><td>80 adults aged 40&ndash;65</td><td>300, 600 or 900 mg/day</td><td>60 days</td><td>Blood NAD+ rose; 600 and 900 mg groups walked farther in 6 minutes; insulin sensitivity unchanged</td></tr>
<tr><td>Kim</td><td>108 adults aged 65+</td><td>250 mg/day</td><td>12 weeks</td><td>Sleep, fatigue and physical performance no different from placebo</td></tr>
<tr><td>Morita</td><td>17 postmenopausal women aged 50&ndash;80</td><td>300 mg/day</td><td>8 weeks</td><td>No placebo group, so results can&rsquo;t be separated from chance or other changes</td></tr>
</table>

<h2>Do NR supplements work better?</h2>
<p>NR has its own set of trials, with similar results: NAD+ goes up, health measures mostly don&rsquo;t move.</p>
<ul>
<li><b>Healthy older adults (2018, <i>Nature Communications</i>):</b> 24 lean, healthy men and women aged 55 to 79 took NR (500 mg twice a day) and a placebo for 6 weeks each, in random order. NAD+ in blood cells rose about 60%. Blood pressure and artery stiffness trended down, but not significantly once the researchers accounted for testing many outcomes. The maker of the NR supplied the capsules and some funding.</li>
<li><b>Men with obesity (2018, <i>American Journal of Clinical Nutrition</i>):</b> 40 sedentary men aged 40 to 70 took 2,000 mg of NR a day or a placebo for 12 weeks. NR didn&rsquo;t improve insulin sensitivity, blood sugar or body composition. The authors noted the results may not apply to women.</li>
<li><b>Older men (reviewed 2023):</b> in 12 men aged 70 to 80 taking NR for 3 weeks, NAD+ in muscle didn&rsquo;t change, and neither did muscle function or strength, though some inflammation markers in blood fell.</li>
</ul>

<h2>Are NMN and NAD+ supplements safe?</h2>
<p>In the trials so far, both were generally well tolerated. The 2023 review reports NR given at up to 2,000 mg a day for up to 20 weeks, and NMN at up to 2,000 mg a day for 4 weeks, without serious safety problems. In the 12-week trial in men with obesity, minor effects such as itching, sweating, bloating and stool changes were reported by 4 people on NR and 2 on placebo.</p>
<p><b>&ldquo;Safe in short trials&rdquo; isn&rsquo;t the same as safe for years.</b> The trials so far have lasted weeks to a few months, not years. Talk to your clinician before starting either, especially if you take medication or manage a health condition.</p>

<h2>Is NMN legal to sell as a supplement? What the FDA says</h2>
<p>NMN&rsquo;s status has flipped:</p>
<ul>
<li><b>November 2022:</b> the FDA took the position that NMN could not be sold as a dietary supplement, because it had been studied as a drug first.</li>
<li><b>March 2023:</b> the Natural Products Association and the Alliance for Natural Health USA petitioned the FDA to reverse that.</li>
<li><b>September 29, 2025:</b> the FDA concluded that NMN is not excluded from the definition of a dietary supplement, because there was evidence it had been sold as one in the US before the drug research began.</li>
</ul>
<p><b>This was a legal decision, not a safety or effectiveness review.</b> The FDA&rsquo;s letter says NMN&rsquo;s status doesn&rsquo;t turn on safety, and earlier FDA responses on NMN were not findings that it is safe.</p>

<h2>The honest bottom line on NMN and NR</h2>
<p>NMN and NR do what they claim at the most basic level: they raise NAD+ in blood. <b>What hasn&rsquo;t been shown is that this makes people healthier in ways they&rsquo;d feel or that would matter long-term.</b> The positive results are small, scattered and often not repeated, and most trials lasted a few weeks.</p>
<ul>
<li><b>Blood sugar:</b> one small trial in postmenopausal women with prediabetes found better muscle insulin sensitivity; a larger NR trial in men found no change.</li>
<li><b>Muscle and strength:</b> mixed. Some trials found small gains in walking or grip, others none. Strength training has far better evidence; see <a href="/bones/strength-training-bone-density-menopause/">strength training for bone density around menopause</a>.</li>
<li><b>Fitness and heart:</b> no consistent benefit. Our guide to <a href="/fitness/vo2-max-women/">VO2 max for women</a> covers what does move cardiovascular fitness.</li>
</ul>
<p>Questions to ask your clinician: Is there any reason this could interact with my medications? Would I be better served by checking blood sugar, cholesterol or blood pressure first? For comparison, see our evidence checks on <a href="/supplements/urolithin-a-evidence/">urolithin A</a> and <a href="/supplements/creatine-for-women-over-40/">creatine for women over 40</a>, or browse all <a href="/supplements/">Supplements</a>.</p>""",
 [("Yoshino M, Yoshino J, Kayser BD, et al. Nicotinamide mononucleotide increases muscle insulin sensitivity in prediabetic women. Science, 2021;372(6547):1224&ndash;1229 (NCT03151239)", "https://profiles.wustl.edu/en/publications/nicotinamide-mononucleotide-increases-muscle-insulin-sensitivity-/"),
  ("Dollerup OL, Christensen B, Svart M, et al. A randomized placebo-controlled clinical trial of nicotinamide riboside in obese men: safety, insulin-sensitivity, and lipid-mobilizing effects. Am J Clin Nutr, 2018;108(2):343&ndash;353", "https://www.sciencedirect.com/science/article/pii/S0002916522029409"),
  ("Freeberg KA, Udovich CC, Martens CR, Seals DR, Craighead DH. Dietary Supplementation With NAD+-Boosting Compounds in Humans: Current Knowledge and Future Directions. J Gerontol A Biol Sci Med Sci, 2023;78(12):2435&ndash;2448", "https://academic.oup.com/biomedgerontology/article/78/12/2435/7126788"),
  ("NIH Research Matters. Supplement improves glucose metabolism in women&rsquo;s muscle (May 11, 2021)", "https://www.nih.gov/news-events/nih-research-matters/supplement-improves-glucose-metabolism-womens-muscle"),
  ("U.S. Food and Drug Administration. Response to citizen petition FDA-2023-P-0872 on the regulatory status of NMN (September 29, 2025)", "https://downloads.regulations.gov/FDA-2023-P-0872-2754/attachment_1.pdf"),
  ("U.S. Food and Drug Administration. Letter on NMN new dietary ingredient notifications NDIN 1240 and 1247 (December 2, 2025)", "https://downloads.regulations.gov/FDA-2022-S-0023-0068/attachment_1.pdf"),
  ("University of Colorado Boulder (press release). A pill that staves off aging? It&rsquo;s on the horizon (March 28, 2018), on Martens et al., Nature Communications 2018", "https://www.colorado.edu/today/2018/03/28/pill-staves-aging-its-horizon")]),


article("/hair/minoxidil-for-women/", "/hair/", "Hair",
 "Minoxidil for Women: Topical vs Oral, What Trials Show",
 "Minoxidil for women: topical vs oral, what the trials show",
 "Topical minoxidil is the only FDA-approved drug for female pattern hair loss. What trials found, the early shed, and what&rsquo;s known about oral pills.",
 "2026-11-15",
 "If your part is widening or your ponytail feels thinner, minoxidil is probably the first treatment you&rsquo;ll hear about. It comes as a scalp foam or solution, and sometimes as a low-dose pill. Here&rsquo;s what the labels and trials say about each.",
 "Topical minoxidil is the only medicine the FDA has approved for female pattern hair loss. In a 48-week trial of 381 women, both the 5% and 2% solutions beat placebo, and MedlinePlus says it regrows hair in about 1 in 4 or 5 women and slows loss in most. <b>Low-dose oral minoxidil is used off-label for hair loss: small trials in women look promising, but it isn&rsquo;t FDA-approved for this use and has different side effects.</b>",
 "human-trial",
 [("Best evidence", "A 48-week randomized, double-blind, placebo-controlled trial of 381 women (Lucky et al., 2004) for topical minoxidil; small randomized trials summarized in a 2023 review for oral minoxidil"),
  ("Women included?", "Yes. All the hair-loss trials described here studied women with female pattern hair loss; the topical trial enrolled women aged 18&ndash;49"),
  ("Dose or protocol tested", "Topical: 5% or 2% solution twice daily for 48 weeks. Oral (off-label): 0.25 mg to 1.25 mg a day for 6 to 24 months in the trials reviewed"),
  ("Bottom line", "Topical minoxidil has FDA approval and placebo-controlled evidence in women. Oral minoxidil is promising but off-label, with smaller and shorter studies. Both only work while you keep using them")],
 """<h2>What is minoxidil, and how is it approved for women?</h2>
<p>Minoxidil is also a prescription blood pressure pill, and extra hair growth is a well-known side effect of the tablets. The two forms have very different official status:</p>
<ul>
<li><b>Topical minoxidil</b> (foam or solution, sold over the counter). According to MedlinePlus, the National Library of Medicine&rsquo;s health site, it&rsquo;s the only medicine the FDA has approved for female pattern hair loss. MedlinePlus notes that the 2% solution or 5% foam is what&rsquo;s used for women.</li>
<li><b>Oral minoxidil</b> (prescription tablets). The FDA label approves it only for severe high blood pressure that hasn&rsquo;t responded to a diuretic plus two other blood pressure drugs. Using it for hair loss is off-label, a 2023 review in <i>Skin Appendage Disorders</i> confirms.</li>
</ul>
<p>Female pattern hair loss is gradual thinning over the top of the head, usually with the front hairline kept. If your loss looks different, start with <a href="/hair/female-hair-loss-causes/">the main causes of hair loss in women</a>. <b>Minoxidil is labeled for pattern thinning, not for sudden or patchy loss.</b></p>

<h2>Topical minoxidil for women: what the trial found</h2>
<p>The largest placebo-controlled trial in women was published in the <i>Journal of the American Academy of Dermatology</i> in 2004 (Lucky et al.).</p>
<ul>
<li><b>Who:</b> 381 women aged 18 to 49 with female pattern hair loss, at multiple centers.</li>
<li><b>Design:</b> randomized and double-blind. 153 women used 5% minoxidil solution, 154 used 2%, and 74 used a placebo solution, each twice a day.</li>
<li><b>How long:</b> 48 weeks.</li>
<li><b>Measured:</b> the change in the count of non-fine (nonvellus) hairs, plus the women&rsquo;s own and the investigators&rsquo; ratings of growth.</li>
<li><b>Found:</b> 5% beat placebo on all three measures. 2% beat placebo on hair count and investigator rating, but not on the women&rsquo;s own rating. Women rated 5% as more helpful than 2%.</li>
</ul>
<p>Itching, scalp irritation and unwanted hair growth on the face or body were more common with 5% than with 2% or placebo. The authors found no signs of effects elsewhere in the body. The trial was funded by Pfizer (formerly Pharmacia and Upjohn).</p>
<p>MedlinePlus puts the real-world picture plainly: <b>minoxidil may regrow hair in about 1 in 4 or 5 women, and may slow or stop loss in most.</b> It slows thinning more reliably than it restores a full head of hair.</p>

<h2>The shedding phase: why hair can fall out at first</h2>
<p>Many women quit in the first weeks because they see more hair in the brush. The consumer leaflet on a 5% foam for women, posted on the NIH&rsquo;s DailyMed label database, warns that shedding may increase for up to 2 weeks after starting. It calls this expected and temporary, and says to see a doctor if it goes on longer.</p>
<p>Results take patience. The same label says regrowth may show at about 3 months, and some women need at least 6 months. MedlinePlus says to allow at least 4 months, and possibly up to a year. The label also advises stopping and asking a doctor if there&rsquo;s no regrowth after 6 months.</p>
<p><b>Minoxidil works only while you use it.</b> The label says regrown hair is likely to be lost within 3 to 4 months of stopping.</p>

<h2>Who the label says shouldn&rsquo;t use topical minoxidil</h2>
<p>The over-the-counter label for women lists several situations where it shouldn&rsquo;t be used without a doctor, because the hair loss may have another cause:</p>
<ul>
<li>Hair loss that is sudden, patchy or linked to childbirth, or a cause you don&rsquo;t know</li>
<li>No family history of hair loss</li>
<li>A red, inflamed, infected, irritated or painful scalp</li>
<li>Under 18, or using other medicines on the scalp</li>
<li>Heart disease (ask a doctor first)</li>
<li>Pregnancy or breastfeeding (the label says it may be harmful)</li>
</ul>
<p>It also says to stop and ask a doctor for chest pain, a fast heartbeat, faintness or dizziness, sudden weight gain, swollen hands or feet, scalp irritation, or unwanted facial hair. Infants have grown extra hair after skin contact with a caregiver&rsquo;s treated scalp; the label says it went away.</p>

<h2>Oral minoxidil for women: what&rsquo;s known so far</h2>
<p>Low-dose oral minoxidil, often called LDOM, is prescribed off-label for hair loss. The 2023 review by Gupta and colleagues summarizes the trials in women with pattern hair loss:</p>
<table>
<tr><th>Study</th><th>Design</th><th>What was compared</th><th>Result</th></tr>
<tr><td>Ramos et al., 2020</td><td>Randomized, open-label (not blinded), 24 weeks</td><td>1 mg oral vs 5% topical</td><td>Trend favoring oral; difference not statistically significant</td></tr>
<tr><td>Vahabi-Amlashi et al., 2021</td><td>Randomized pilot, 6 months</td><td>0.25 mg oral vs 2% topical</td><td>No significant difference</td></tr>
<tr><td>Nascimento e Silva et al., 2022</td><td>Randomized, double-blind, 24 weeks</td><td>0.25 mg vs 1 mg oral</td><td>1 mg more effective</td></tr>
</table>
<p>These are the doses the studies tested, not recommendations. <b>None of these trials compared oral minoxidil with a placebo, and all were small and lasted a year or less.</b></p>

<h3>Side effects of oral minoxidil</h3>
<ul>
<li><b>Unwanted hair growth</b> (on the face or body) is the most common. In a 1,404-patient study summarized in the review, 20.1% of women had it, at a median dose of about 1.1 mg a day.</li>
<li><b>Dizziness, fast heartbeat and fluid swelling</b> were less common. In one small study, 3 of 12 women had swelling of the limbs.</li>
<li><b>Pregnancy:</b> the review says oral minoxidil isn&rsquo;t recommended in pregnancy or breastfeeding, and lists heart rhythm problems, kidney disease and low blood pressure among reasons for caution.</li>
</ul>
<p>For context, the FDA label for the blood pressure version carries a boxed warning about fluid building up around the heart. At blood pressure doses, about 3% of patients not on dialysis developed it, temporary swelling occurred in 7%, and about 80% had extra body hair growth. Those numbers come from people with severe high blood pressure, not from women on low doses for hair. <b>They&rsquo;re why oral minoxidil needs a prescriber who knows your heart and blood pressure history.</b></p>

<h2>Topical vs oral minoxidil for women at a glance</h2>
<table>
<tr><th></th><th>Topical (foam or solution)</th><th>Oral (low-dose tablet)</th></tr>
<tr><td>FDA status for hair loss</td><td>Approved for women, over the counter</td><td>Not approved; off-label prescription</td></tr>
<tr><td>Best evidence in women</td><td>48-week placebo-controlled trial, 381 women</td><td>Small randomized trials, 24 weeks to 6 months</td></tr>
<tr><td>Common side effects</td><td>Scalp itching, dryness, flaking, irritation; facial hair</td><td>Facial and body hair; less often dizziness, fast heartbeat, swelling</td></tr>
<tr><td>Pregnancy or breastfeeding</td><td>Label says it may be harmful</td><td>Review says it isn&rsquo;t recommended</td></tr>
</table>

<h2>What this means for you</h2>
<p>If a dermatologist confirms female pattern hair loss, topical minoxidil is the treatment with FDA approval and placebo-controlled evidence in women. Expect a possible shed early on, give it months, and know it&rsquo;s a long-term commitment. Oral minoxidil is a reasonable thing to ask about, but it&rsquo;s off-label and its evidence is thinner. For other options with lighter evidence, see <a href="/hair/rosemary-oil-hair-growth/">what the rosemary oil trial found</a>, and for lab causes worth ruling out first, <a href="/hair/iron-ferritin-hair-loss/">iron, ferritin and hair loss</a>.</p>
<p>Questions to ask a board-certified dermatologist:</p>
<ul>
<li>Is this female pattern hair loss, or could shedding or another cause be part of it?</li>
<li>Is topical minoxidil a good fit for me, and how will we judge whether it&rsquo;s working?</li>
<li>Would oral minoxidil make sense for me, given my blood pressure, heart health and other medicines?</li>
<li>What side effects should make me call you?</li>
<li>What if I&rsquo;m planning a pregnancy or breastfeeding?</li>
</ul>
<p>Don&rsquo;t start, stop or change any prescription without the clinician who prescribes it. More in the <a href="/hair/">Hair</a> hub and our guide to <a href="/hair/hair-thinning-perimenopause/">hair thinning in perimenopause</a>.</p>""",
 [("Lucky AW, Piacquadio DJ, Ditre CM, et al. A randomized, placebo-controlled trial of 5% and 2% topical minoxidil solutions in the treatment of female pattern hair loss. J Am Acad Dermatol, 2004;50(4):541&ndash;553 (abstract via UT Southwestern)", "https://utsouthwestern.elsevierpure.com/en/publications/a-randomized-placebo-controlled-trial-of-5-and-2-topical-minoxidi/"),
  ("Gupta AK, Talukder M, Shemer A, Piraccini BM, Tosti A. Low-Dose Oral Minoxidil for Alopecia: A Comprehensive Review. Skin Appendage Disord, 2023;9(6):423&ndash;437", "https://pmc.ncbi.nlm.nih.gov/articles/PMC10806356/"),
  ("DailyMed (National Library of Medicine). Label: Minoxidil 5% (for women) topical foam, Drug Facts and consumer information", "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=dbda95f2-11a8-4b2f-af45-b791342fff70"),
  ("U.S. Food and Drug Administration. Loniten (minoxidil tablets) prescribing information, revised January 2015", "https://www.accessdata.fda.gov/drugsatfda_docs/label/2015/018154s026lbl.pdf"),
  ("MedlinePlus Medical Encyclopedia. Female pattern baldness (reviewed January 28, 2026)", "https://medlineplus.gov/ency/article/001173.htm"),
  ("MedlinePlus Drug Information. Minoxidil Topical", "https://medlineplus.gov/druginfo/meds/a689003.html")]),


article("/hair/iron-ferritin-hair-loss/", "/hair/", "Hair",
 "Iron, Ferritin and Hair Loss in Women: What Labs Mean",
 "Iron, ferritin and hair loss: what your labs mean",
 "How low iron is linked to hair shedding in women, what a ferritin test measures, why the cutoffs differ, and why iron pills without testing carry risks.",
 "2026-11-15",
 "Ferritin is one of the first blood tests many women get when their hair starts shedding. The results can be confusing: a number your lab calls normal may be one some experts call low. Here&rsquo;s what the test measures and what the research does and doesn&rsquo;t show.",
 "Studies pooled in a 2022 meta-analysis found that women with non-scarring hair loss have lower ferritin (stored iron) on average than women without it, but these studies show a link, not that low iron causes hair loss or that iron fixes it. <b>Ferritin cutoffs differ between labs and guidelines, so ask what threshold your clinician is using, and don&rsquo;t take iron without testing.</b>",
 "human-obs",
 [("Best evidence", "A 2022 meta-analysis of 36 observational studies (10,029 participants: 6,641 women with hair loss and 3,388 controls); a 2008 clinic study of 181 women"),
  ("Women included?", "Yes. The meta-analysis included only women; the clinic study was all women, average age about 42"),
  ("Dose or protocol tested", "None. These studies measured iron levels; they didn&rsquo;t test iron supplements"),
  ("Bottom line", "Low iron stores are linked with hair loss in women, but whether raising them helps hair hasn&rsquo;t been settled by controlled trials. Testing comes first")],
 """<h2>What does ferritin measure?</h2>
<p>Ferritin is a protein that stores iron. MedlinePlus, the National Library of Medicine&rsquo;s health site, explains that a ferritin blood test indirectly shows how much iron your body has in reserve.</p>
<p>Iron runs low in stages, according to the NIH Office of Dietary Supplements (ODS). First the stores drain, and ferritin drops. Next, red blood cell production starts to suffer. Only at the last stage does iron-deficiency anemia show up, with low hemoglobin. ODS notes that ferritin can pick up iron depletion at an early stage.</p>
<p><b>That&rsquo;s why a normal blood count doesn&rsquo;t rule out low iron.</b> A StatPearls review on NIH&rsquo;s NCBI Bookshelf makes the same point: hemoglobin falls late.</p>
<p>Your clinician may also order serum iron, total iron-binding capacity and transferrin saturation, which help fill in the picture.</p>

<h2>Is low iron linked to hair loss in women?</h2>
<p>Hair loss is on the symptom lists for iron deficiency in both MedlinePlus and StatPearls. The bigger question is how strong the link is.</p>
<p>The largest analysis is a 2022 meta-analysis in <i>Skin Appendage Disorders</i> (Treister-Goltzman and colleagues):</p>
<ul>
<li><b>Who:</b> 36 studies published from 1988 to 2019, with 10,029 participants: 6,641 women with non-scarring hair loss and 3,388 women without it.</li>
<li><b>Design:</b> 21 case-control and 15 cohort studies, all observational.</li>
<li><b>Measured:</b> ferritin levels and how often iron-deficiency anemia occurred.</li>
<li><b>Found:</b> women with hair loss had lower ferritin on average than women without it, including in a subgroup of premenopausal women. Iron-deficiency anemia wasn&rsquo;t more common in women with hair loss.</li>
</ul>
<p>The limits matter. The studies varied a lot in their results and used different definitions of iron deficiency. Most came from specialist referral clinics, which may not reflect women in general. <b>This kind of evidence shows a link; it can&rsquo;t show that low iron causes hair loss or that iron supplements fix it.</b></p>
<p>Not every study agrees. A 2008 study in <i>Dermatology</i> (Bregy and Tr&uuml;eb) looked at 181 otherwise healthy women seen at a Zurich hair clinic between 2002 and 2005, with female pattern hair loss, diffuse shedding (telogen effluvium), or both. Their average age was about 42. Among women with ferritin above 10 ng/mL, ferritin wasn&rsquo;t related to how much hair was in the shedding phase. The authors concluded iron&rsquo;s role had probably been overestimated and that controlled trials of iron were needed.</p>

<h2>Ferritin levels for hair loss: why the cutoffs differ</h2>
<p>Here&rsquo;s where lab results get confusing. Different sources draw the line for &ldquo;low&rdquo; in different places. Ferritin is reported in ng/mL, which is the same as &micro;g/L.</p>
<table>
<tr><th>Source</th><th>Threshold</th><th>What it&rsquo;s for</th></tr>
<tr><td>MedlinePlus</td><td>13&ndash;150 ng/mL</td><td>Typical normal range for females; ranges vary by lab</td></tr>
<tr><td>StatPearls review (2026)</td><td>Below 30 ng/mL</td><td>Diagnosing absolute iron deficiency; 92% sensitive and 98% specific for absent bone marrow iron</td></tr>
<tr><td>American Gastroenterological Association guideline</td><td>Below 45 ng/mL</td><td>Diagnosing iron deficiency in people who already have anemia</td></tr>
<tr><td>Bregy and Tr&uuml;eb, 2008</td><td>Above 10 ng/mL</td><td>No link with shedding found above this level in their clinic</td></tr>
</table>
<p><b>A ferritin of 20 could be &ldquo;normal&rdquo; on one lab report and &ldquo;iron deficient&rdquo; by another standard.</b> Neither number was set specifically for hair. It&rsquo;s fair to ask your clinician which cutoff they&rsquo;re using and why.</p>
<p>One more wrinkle: ferritin rises with inflammation. StatPearls notes it can be raised by chronic disease, inflammatory states and cancer, and MedlinePlus lists liver disease, autoimmune conditions such as rheumatoid arthritis and an overactive thyroid among causes of high ferritin. <b>So a normal ferritin can hide low iron if inflammation is pushing it up.</b> That&rsquo;s one reason clinicians look at several iron tests together.</p>

<h2>Why women in their 30s and 40s run low on iron</h2>
<ul>
<li><b>Periods.</b> MedlinePlus lists heavy menstrual bleeding as a cause of low ferritin, and StatPearls names menstrual blood loss among the most common causes of iron deficiency in developed countries.</li>
<li><b>Higher needs.</b> ODS sets the recommended intake at 18 mg a day for women 19 to 50, dropping to 8 mg a day from age 51. StatPearls notes that average intake for women of reproductive age is about 13 mg a day.</li>
<li><b>Pregnancy and breastfeeding</b> raise iron needs, according to MedlinePlus.</li>
<li><b>Absorption problems</b> such as celiac disease, Crohn disease or gastric bypass surgery.</li>
<li><b>Diet.</b> Eating little iron-rich food, including some strict vegetarian diets.</li>
</ul>
<p>Low iron in an adult can also be a sign of hidden bleeding in the gut, which is why MedlinePlus lists tests to look for a source. It&rsquo;s a reason to find out <i>why</i> iron is low, not just to top it up.</p>

<h2>The risks of taking iron for hair without testing</h2>
<p>MedlinePlus says providers usually measure iron levels before starting supplements. There are good reasons:</p>
<ul>
<li><b>Iron overload.</b> Hereditary hemochromatosis makes the body store too much iron. ODS says about 1 in 10 white people carry the most common gene variant, and about 4.4 per 1,000 have two copies and the condition. It&rsquo;s much less common in other groups. Extra iron is the last thing they need.</li>
<li><b>Side effects.</b> ODS says intakes of 45 mg a day or more can cause nausea and constipation. That 45 mg is the official upper limit for adults from food and supplements combined.</li>
<li><b>Medicine interactions.</b> ODS notes that iron can make levothyroxine (a thyroid medicine) and levodopa (a Parkinson&rsquo;s medicine) less effective, and that heartburn drugs called proton pump inhibitors can reduce iron absorption.</li>
<li><b>Children.</b> ODS reports that at least 43 U.S. children died from swallowing high-dose iron supplements between 1983 and 2000. Iron belongs out of reach.</li>
</ul>
<p>Whether you need iron, and how much, is a question for your clinician based on your results. Talk to your clinician before starting any iron supplement.</p>

<h2>What this means for you</h2>
<p>If you&rsquo;re shedding, a ferritin test is a reasonable thing to ask about, along with the other checks a dermatologist may suggest, such as thyroid tests. Low iron is common, treatable and worth finding for its own sake. Just know that the hair evidence is observational and the cutoffs aren&rsquo;t agreed. For the full picture of causes, see <a href="/hair/female-hair-loss-causes/">hair loss in women: causes and how to tell them apart</a>, plus <a href="/hair/telogen-effluvium/">telogen effluvium</a> and <a href="/hair/thyroid-hair-loss/">thyroid and hair loss</a>.</p>
<p>Questions to ask your doctor or a board-certified dermatologist:</p>
<ul>
<li>What was my ferritin, and what cutoff are you using to call it low?</li>
<li>Should we also check transferrin saturation, a blood count or a marker of inflammation?</li>
<li>If my iron is low, what&rsquo;s causing it? Do my periods or gut need a closer look?</li>
<li>Would iron make sense for me, and how would we recheck it?</li>
<li>Could iron interact with any medicine I take?</li>
</ul>
<p>More in the <a href="/hair/">Hair</a> hub, including <a href="/hair/minoxidil-for-women/">minoxidil for women</a>.</p>""",
 [("Treister-Goltzman Y, Yarza S, Peleg R. Iron Deficiency and Nonscarring Alopecia in Women: Systematic Review and Meta-Analysis. Skin Appendage Disord, 2022;8(2):83&ndash;92", "https://karger.com/sad/article/8/2/83/826740/Iron-Deficiency-and-Nonscarring-Alopecia-in-Women"),
  ("Bregy A, Tr&uuml;eb RM. No Association between Serum Ferritin Levels &gt;10 &micro;g/l and Hair Loss Activity in Women. Dermatology, 2008;217(1):1&ndash;6", "https://karger.com/drm/article/217/1/1/112693/No-Association-between-Serum-Ferritin-Levels-gt-10"),
  ("NIH Office of Dietary Supplements. Iron: Fact Sheet for Health Professionals", "https://ods.od.nih.gov/factsheets/Iron-HealthProfessional/"),
  ("Hanif N, Rout P, Anwer F. Iron Deficiency and Microcytic Hypochromic Anemia. StatPearls, NCBI Bookshelf (updated February 21, 2026)", "https://www.ncbi.nlm.nih.gov/sites/books/NBK560876/"),
  ("Ko CW, et al. AGA Clinical Practice Guidelines on the Gastrointestinal Evaluation of Iron Deficiency Anemia. Gastroenterology", "https://www.gastrojournal.org/article/S0016-5085(20)34847-2/fulltext"),
  ("MedlinePlus Medical Encyclopedia. Ferritin blood test (reviewed January 10, 2026)", "https://medlineplus.gov/ency/article/003490.htm"),
  ("MedlinePlus Medical Encyclopedia. Iron deficiency anemia (reviewed April 1, 2025)", "https://medlineplus.gov/ency/article/000584.htm")]),


article("/foundations/deep-sleep-after-35/", "/foundations/", "Sleep &amp; Foundations",
 "Deep Sleep After 35: What Changes and What Helps",
 "Deep sleep after 35: what changes and what helps",
 "How deep sleep changes with age and menopause, why night waking rises in midlife, and what the evidence says about CBT-I, melatonin and sleep pills.",
 "2026-11-16",
 "If your sleep feels thinner than it did at 30, you&rsquo;re not imagining it. But the story is more specific than &ldquo;menopause steals your deep sleep.&rdquo; Here&rsquo;s what the sleep-lab studies actually show, and what has been tested to help.",
 "Deep sleep shrinks gradually across adulthood, but sleep-lab studies of midlife women haven&rsquo;t found that menopause itself wipes it out. The bigger midlife change is waking up more, often tied to hot flashes. <b>For ongoing insomnia, the American College of Physicians recommends cognitive behavioral therapy for insomnia (CBT-I) as the first treatment, and a trial in women with hot flashes found it worked.</b>",
 "human-trial",
 [("Best evidence", "A 2016 randomized trial of phone-based CBT-I in 106 women aged 40&ndash;65 with hot flashes and insomnia; a 2004 meta-analysis of 65 sleep-lab studies (3,577 people); a 2016 ACP clinical guideline"),
  ("Women included?", "Yes. The CBT-I trial and the menopause sleep-lab studies enrolled only women. The age meta-analysis included both sexes, and its abstract doesn&rsquo;t report results by sex"),
  ("Protocol tested", "Six 20&ndash;30 minute CBT-I phone sessions over 8 weeks, compared with phone-based menopause education"),
  ("Bottom line", "Some loss of deep sleep is a normal part of aging. Night waking in midlife is common and treatable, and CBT-I has the strongest evidence")],
 """<h2>What is deep sleep?</h2>
<p>Deep sleep is stage 3 of non-REM sleep, also called slow-wave sleep. The National Institute of Neurological Disorders and Stroke (NINDS) describes it as the stage when brain waves are slowest, heartbeat and breathing reach their lowest levels of the night, and you may be hard to wake. It comes in longer stretches in the first half of the night.</p>
<p><b>NINDS calls it the deep sleep you need to feel refreshed in the morning.</b> That&rsquo;s why losing some of it gets so much attention.</p>

<h2>Does deep sleep decrease with age?</h2>
<p>Yes, gradually. The largest summary is a 2004 meta-analysis in <i>Sleep</i> (Ohayon and colleagues):</p>
<ul>
<li><b>Who:</b> 65 sleep-lab studies published from 1960 to 2003, covering 3,577 healthy people aged 5 to 102.</li>
<li><b>Design:</b> a meta-analysis of overnight sleep recordings (polysomnography).</li>
<li><b>Found:</b> in adults, the share of the night spent in slow-wave sleep fell with age. Total sleep time and sleep efficiency (the share of time in bed actually asleep) also fell, and time awake after first falling asleep rose.</li>
</ul>
<p>The abstract doesn&rsquo;t report results separately for women, so it can&rsquo;t say whether the pattern differs by sex. <b>The takeaway: a slow decline in deep sleep is a normal part of getting older, not a sign something is wrong.</b></p>

<h2>Deep sleep and menopause: what sleep-lab studies show</h2>
<p>Here&rsquo;s the surprise. When researchers recorded the same women&rsquo;s sleep before and after the menopause transition, deep sleep didn&rsquo;t collapse.</p>
<table>
<tr><th>Study</th><th>Who</th><th>What they found</th></tr>
<tr><td>SWAN sleep study (Matthews and colleagues, 2021)</td><td>159 US women, average age about 51, recorded at home 2&ndash;3 nights, then again about 3.6 years later</td><td>Deep-sleep brain-wave activity didn&rsquo;t change differently in women who reached postmenopause. Faster brain-wave activity during non-REM sleep did rise in that group, and hot flashes didn&rsquo;t explain it.</td></tr>
<tr><td>Finnish 10-year follow-up (Kalleinen and colleagues, 2021)</td><td>57 women, age 46 at the start and about 57 at follow-up, not on hormone therapy</td><td>Slow-wave sleep went from 17.9% to 26.1% of the night. The authors concluded the changes seemed more tied to age than to menopause.</td></tr>
</table>
<p>Both studies are small, and the Finnish team used older scoring rules for sleep stages. Still, <b>neither found that menopause itself drains deep sleep.</b> For more on how the transition affects the body, see our look at <a href="/news/menopause-physiological-cliff-study/">the menopause &ldquo;cliff&rdquo; study</a>.</p>

<h2>Why does sleep feel worse in perimenopause?</h2>
<p>What women report changes more than what the lab measures. The SWAN study followed 3,045 women aged 42 to 52 through seven yearly check-ins (Kravitz and colleagues, 2008). More frequent hot flashes and night sweats were linked to higher odds of every kind of sleep trouble they asked about. Falling estrogen was linked to trouble falling and staying asleep.</p>
<p>The National Institute on Aging (NIA) lists the usual suspects:</p>
<ul>
<li><b>Hot flashes and night sweats.</b> NIA notes some research suggests waking up may trigger a hot flash, rather than the other way around.</li>
<li><b>Mood changes,</b> especially depression.</li>
<li><b>Life load:</b> aging parents, kids, heavier work demands.</li>
</ul>
<p><b>So the midlife problem is often broken sleep, not missing deep sleep.</b> That matters, because it points to different fixes.</p>

<h2>Better sleep after 35: what has evidence</h2>
<h3>CBT-I comes first</h3>
<p>Cognitive behavioral therapy for insomnia (CBT-I) is a short, structured program. It combines sleep-focused cognitive therapy, behavior changes such as sleep restriction (limiting time in bed to time actually asleep, then widening it) and stimulus control (using the bed only for sleep), plus sleep habits education.</p>
<p>In 2016, the American College of Physicians (ACP) issued a strong recommendation, based on moderate-quality evidence, that all adults with chronic insomnia get CBT-I as the first treatment. It can be done in person, in groups, by phone, online or with self-help books.</p>
<p>It has been tested in women like our readers. The MsFLASH trial (McCurry and colleagues, <i>JAMA Internal Medicine</i>, 2016):</p>
<ul>
<li><b>Who:</b> 106 women aged 40 to 65 (average about 55), perimenopausal or postmenopausal, with at least two hot flashes a day and insomnia.</li>
<li><b>Design:</b> randomized trial. Six 20&ndash;30 minute CBT-I phone sessions over 8 weeks, compared with phone sessions of menopause education.</li>
<li><b>Measured:</b> insomnia severity and sleep quality, at 8 and 24 weeks.</li>
<li><b>Found:</b> at 8 weeks, 70% of the CBT-I group scored in the no-insomnia range, versus 24% of the education group. At 24 weeks it was 84% versus 43%.</li>
</ul>
<p>CBT-I didn&rsquo;t reduce how often hot flashes happened, but women said hot flashes got in the way of daily life less. <b>CBT-I improved sleep even while hot flashes kept coming.</b> NIA suggests looking for a therapist with experience treating women in the menopause transition.</p>

<h3>Exercise and regular habits</h3>
<p>In a SWAN analysis of 339 women around age 52 (Kline and colleagues, 2013), those who did more sports and exercise had more deep-sleep brain-wave activity, better sleep efficiency and lower odds of insomnia. That study was a snapshot in time, so it shows a link, not cause and effect. See our guide to <a href="/fitness/vo2-max-women/">VO2 max for women</a> and <a href="/bones/strength-training-bone-density-menopause/">strength training in menopause</a> for ways to build activity in.</p>
<p>The CDC and NIA give overlapping sleep habit advice:</p>
<ul>
<li>Go to bed and get up at the same time every day.</li>
<li>Keep the bedroom quiet and comfortably cool.</li>
<li>Turn off screens at least 30 minutes before bed (CDC).</li>
<li>Limit caffeine later in the day, and avoid large meals and alcohol before bed. NIA notes that even small amounts of alcohol can make it harder to stay asleep.</li>
<li>Skip late-afternoon or evening naps (NIA).</li>
</ul>
<p>For how much sleep to aim for, the CDC says adults 18 to 60 need 7 or more hours a night.</p>

<h2>What about melatonin and sleep pills?</h2>
<p><b>Melatonin.</b> The National Center for Complementary and Integrative Health (NCCIH) says there isn&rsquo;t enough strong evidence to recommend melatonin for chronic insomnia, a conclusion shared by the American Academy of Sleep Medicine (2017) and the ACP (2016). It&rsquo;s sold as a dietary supplement in the US, so labels can be off: a 2023 study cited by NCCIH found 22 of 25 melatonin gummies were mislabeled, with amounts from 74% to 347% of the label. Long-term safety data are lacking. Talk to your clinician before trying it, especially if you take a blood thinner.</p>
<p><b>Prescription sleep medicines.</b> The ACP says medication can be considered, through shared decision-making about benefits, harms and costs, when CBT-I alone hasn&rsquo;t worked, and for short-term use. In 2019 the FDA added a boxed warning to eszopiclone, zaleplon and zolpidem after rare but serious injuries and deaths from sleepwalking, sleep driving and other activities done while not fully awake. NIA says neither melatonin nor prescription sleep medicines is a fix for insomnia, and neither should be used long term.</p>
<p>Supplements like magnesium are popular too; we&rsquo;ll cover the evidence in <a href="/supplements/magnesium-glycinate-vs-threonate/">magnesium glycinate vs. L-threonate</a>.</p>

<h2>The honest bottom line</h2>
<p>A slow drop in deep sleep is part of aging, and wearables that show &ldquo;low deep sleep&rdquo; may be measuring something that&rsquo;s normal for your age (we&rsquo;re checking <a href="/health-trackers/sleep-tracker-accuracy/">how accurate sleep trackers are</a>). The midlife problem that&rsquo;s most common, and most treatable, is waking up and not getting back to sleep.</p>
<p>Questions to bring to your clinician:</p>
<ul>
<li>Could hot flashes, mood, a medicine or another sleep disorder be behind my waking?</li>
<li>Is CBT-I a fit for me, and how do I find a trained provider or program?</li>
<li>If we consider a sleep medicine or melatonin, what are the risks for me, and for how long?</li>
<li>Would treating my menopause symptoms help my sleep?</li>
</ul>
<p>More basics in <a href="/foundations/">Sleep &amp; Foundations</a>.</p>""",
 [("Ohayon MM, Carskadon MA, Guilleminault C, Vitiello MV. Meta-analysis of quantitative sleep parameters from childhood to old age in healthy individuals. Sleep, 2004;27(7):1255&ndash;1273", "https://academic.oup.com/sleep/article/27/7/1255/2696819"),
  ("Matthews KA, et al. Influence of the menopausal transition on polysomnographic sleep characteristics: a longitudinal analysis. Sleep, 2021;44(11):zsab139", "https://academic.oup.com/sleep/article/44/11/zsab139/6291662"),
  ("Kalleinen N, et al. Sleep during menopausal transition: a 10-year follow-up. Sleep, 2021;44(6):zsaa283", "https://academic.oup.com/sleep/article/44/6/zsaa283/6039192"),
  ("Kravitz HM, et al. Sleep disturbance during the menopausal transition in a multi-ethnic community sample of women. Sleep, 2008;31(7):979&ndash;990", "https://academic.oup.com/sleep/article-abstract/31/7/979/2454246"),
  ("McCurry SM, et al. Telephone-based cognitive behavioral therapy for insomnia in perimenopausal and postmenopausal women with vasomotor symptoms: a MsFLASH randomized clinical trial. JAMA Intern Med, 2016;176(7):913&ndash;920", "https://jamanetwork.com/journals/jamainternalmedicine/fullarticle/2522398"),
  ("Kline CE, et al. Consistently high sports/exercise activity is associated with better sleep quality, continuity and depth in midlife women: the SWAN Sleep Study. Sleep, 2013;36(9):1279&ndash;1288", "https://academic.oup.com/sleep/article/36/9/1279/2453863"),
  ("Qaseem A, et al. Management of chronic insomnia disorder in adults: a clinical practice guideline from the American College of Physicians. Ann Intern Med, 2016;165(2):125&ndash;133", "https://www.acpjournals.org/doi/10.7326/M15-2175"),
  ("National Institute on Aging. Sleep Problems and Menopause: What Can I Do?", "https://www.nia.nih.gov/health/menopause/sleep-problems-and-menopause-what-can-i-do"),
  ("National Institute of Neurological Disorders and Stroke. Brain Basics: Understanding Sleep", "https://www.ninds.nih.gov/health-information/public-education/brain-basics/brain-basics-understanding-sleep"),
  ("CDC. About Sleep", "https://www.cdc.gov/sleep/about/index.html"),
  ("NCCIH. Melatonin: What You Need To Know (updated May 2024)", "https://www.nccih.nih.gov/health/melatonin-what-you-need-to-know"),
  ("FDA. Certain prescription insomnia medicines: new boxed warning (April 30, 2019)", "https://www.fda.gov/safety/medical-product-safety-information/certain-prescription-insomnia-medicines-new-boxed-warning-due-risk-serious-injuries-caused")]),


article("/hair/telogen-effluvium/", "/hair/", "Hair",
 "Telogen Effluvium: Sudden Hair Shedding in Women",
 "Telogen effluvium: sudden hair shedding after stress, illness or surgery",
 "Why hair can shed in handfuls months after an illness, surgery or childbirth, how long telogen effluvium lasts, and how it differs from pattern hair loss.",
 "2026-11-17",
 "Hair in the drain, on the pillow, in your hands after a shower, and it seems to come from nowhere. Often the cause happened months earlier. This is telogen effluvium, one of the most common reasons women suddenly shed, and the outlook is usually good.",
 "Telogen effluvium is diffuse shedding that usually starts about 3 months after a shock to the body, such as a high fever, surgery, childbirth, a crash diet or a new medicine. <b>The acute form usually settles on its own once the trigger is gone, and hair regrows, though full recovery can take several months to a year.</b> Shedding that lasts more than 6 months is called chronic and deserves a dermatologist&rsquo;s look.",
 "review",
 [("Best evidence", "Clinical reviews (StatPearls, updated 2024; <i>Cureus</i>, 2020) and a 1996 biopsy study of 355 people with chronic diffuse shedding"),
  ("Women included?", "Yes. The 1996 study was 346 women and 9 men; reviews say women are more often affected and more likely to seek care"),
  ("Dose or protocol tested", "None. These sources describe causes, timing and diagnosis, not a treatment trial"),
  ("Bottom line", "Find and fix the trigger; acute shedding is usually self-limited. Long-lasting or patchy loss, or a widening part, needs a dermatologist")],
 """<h2>What is telogen effluvium?</h2>
<p>Each hair on your scalp cycles through a growing phase (anagen), a short transition (catagen) and a resting phase (telogen), after which it falls out and a new one starts. On a typical scalp, about 85 to 90% of hairs are growing and 10 to 15% are resting, according to a StatPearls review on NIH&rsquo;s NCBI Bookshelf and a 2020 review in <i>Cureus</i>. StatPearls puts the growing phase at almost 4 years and the resting phase at about 4 months.</p>
<p>Telogen effluvium happens when a stress on the body pushes many growing hairs into the resting phase at once. A few months later, they all fall out together. <b>It&rsquo;s a nonscarring type of hair loss: StatPearls notes that follicle number and density are typically normal.</b></p>
<p>MedlinePlus, the National Library of Medicine&rsquo;s health site, says most people lose about 50 to 200 hairs a day anyway. With telogen effluvium the loss is spread over the whole scalp rather than in patches.</p>

<h2>What triggers telogen effluvium?</h2>
<p>StatPearls and MedlinePlus list overlapping triggers:</p>
<ul>
<li><b>Illness:</b> high fever, severe infection, serious illness.</li>
<li><b>Major surgery, severe injury or sudden blood loss.</b></li>
<li><b>Childbirth.</b> StatPearls notes falling estrogen after delivery is a common cause in women.</li>
<li><b>Crash dieting or low protein intake.</b></li>
<li><b>Severe emotional stress.</b></li>
<li><b>Thyroid problems and iron deficiency.</b> See <a href="/hair/thyroid-hair-loss/">thyroid and hair loss</a> and <a href="/hair/iron-ferritin-hair-loss/">iron, ferritin and hair loss</a>.</li>
<li><b>Medicines,</b> including retinoids (and excess vitamin A), beta-blockers, blood thinners, some antidepressants and anti-seizure drugs, birth control pills, and suddenly stopping a medicine that contains estrogen.</li>
</ul>
<p>The 2020 <i>Cureus</i> review notes that no cause is found in about a third of acute cases. <b>If you suspect a medicine, don&rsquo;t stop it on your own; ask the clinician who prescribed it.</b></p>

<h2>When does shedding start, and how long does telogen effluvium last?</h2>
<p>This is the part that confuses people. StatPearls says the trigger usually comes about 3 months before the shedding starts, with a range of 1 to 6 months. By then, many people have recovered from the illness or event and don&rsquo;t connect the two.</p>
<table>
<tr><th>Stage</th><th>Typical timing</th><th>Source</th></tr>
<tr><td>Shedding begins after a trigger</td><td>About 3 months (range 1&ndash;6)</td><td>StatPearls</td></tr>
<tr><td>Shedding after childbirth</td><td>2&ndash;4 months after delivery, usually lasting about 2 months</td><td>Rebora, <i>Skin Appendage Disorders</i>, 2016</td></tr>
<tr><td>Shedding tapers off</td><td>Over 6&ndash;8 months</td><td>MedlinePlus</td></tr>
<tr><td>Regrowth restarts</td><td>Can take up to 6 months</td><td>StatPearls</td></tr>
<tr><td>Full density returns</td><td>Several months to a year</td><td>StatPearls</td></tr>
</table>
<p>The <i>Cureus</i> review reports that about 95% of acute cases go into remission. Rebora&rsquo;s 2016 review says shedding after childbirth is commonly followed by complete recovery and rarely becomes chronic.</p>
<p><b>Because regrowth can take up to 6 months to restart, hair can still look thin for a while after the shedding itself has stopped.</b></p>

<h2>Chronic telogen effluvium in women 30 to 60</h2>
<p>When shedding goes on for more than 6 months, it&rsquo;s called chronic telogen effluvium. The defining study is a 1996 paper in the <i>Journal of the American Academy of Dermatology</i> by David Whiting:</p>
<ul>
<li><b>Who:</b> 355 people with diffuse thinning of unknown cause (346 women, 9 men), compared with 412 people with pattern hair loss and 22 people with normal scalps.</li>
<li><b>Design:</b> two small scalp biopsies from each person, examined under the microscope.</li>
<li><b>Found:</b> people with chronic telogen effluvium had about as many hairs as controls (39 vs 40 per sample), and few fine &ldquo;miniaturized&rdquo; hairs, with a terminal-to-vellus ratio of 9:1. People with pattern hair loss had far more fine hairs, a ratio of 1.9:1.</li>
</ul>
<p>Whiting concluded that chronic telogen effluvium usually affects women aged 30 to 60, starts abruptly, with or without a clear trigger, and runs a long, fluctuating course. MedlinePlus likewise notes diffuse thinning with no known cause in some women aged 30 to 60. <b>It can be frustrating, but StatPearls describes the cosmetic outcome as good even when shedding continues.</b></p>

<h2>Telogen effluvium vs female pattern hair loss</h2>
<p>The two can look alike, and they can happen together. Some differences from the sources:</p>
<table>
<tr><th></th><th>Telogen effluvium</th><th>Female pattern hair loss</th></tr>
<tr><td>Onset</td><td>Often abrupt (StatPearls; Whiting)</td><td>Develops as follicles shrink over time (MedlinePlus)</td></tr>
<tr><td>Where</td><td>Diffuse, all over the scalp</td><td>Top and crown, often starting as a widening center part (MedlinePlus)</td></tr>
<tr><td>Hair itself</td><td>Few fine, miniaturized hairs in biopsies (Whiting)</td><td>Shrinking follicles make shorter, finer hairs (MedlinePlus)</td></tr>
</table>
<p>For more on how dermatologists sort out the causes, see <a href="/hair/female-hair-loss-causes/">hair loss in women: causes and how to tell them apart</a>.</p>

<h2>How dermatologists diagnose telogen effluvium</h2>
<ul>
<li><b>History:</b> what happened 1 to 6 months before the shedding started, and your medicines.</li>
<li><b>Pull test:</b> StatPearls says a gentle pull on a small bunch of hair usually brings out at least four hairs during active shedding. It can be normal once shedding has stopped.</li>
<li><b>Hair counts:</b> collecting 100 or more shed hairs in 24 hours suggests telogen effluvium, per StatPearls. The <i>Cureus</i> review describes a wash test that also counts fine hairs to help separate it from pattern hair loss.</li>
<li><b>Blood tests:</b> StatPearls lists iron studies, including ferritin, and a thyroid test (TSH) when symptoms point that way.</li>
<li><b>Biopsy:</b> rarely needed. StatPearls says it confirms telogen effluvium when 25 to 50% of follicles are in the resting phase.</li>
</ul>

<h2>Does anything help telogen effluvium?</h2>
<p>StatPearls describes acute telogen effluvium as self-limited: once the trigger is found and dealt with, hair growth returns. The <i>Cureus</i> review stresses finding and removing the trigger, correcting any deficiency that tests confirm, and keeping a balanced diet and stable weight. <b>StatPearls notes topical minoxidil hasn&rsquo;t been proven effective for telogen effluvium</b>, and treatment for chronic or mixed cases is a decision for a board-certified dermatologist (see <a href="/hair/minoxidil-for-women/">minoxidil for women</a> for the evidence in pattern hair loss).</p>

<h2>What this means for you</h2>
<p>Sudden, all-over shedding a few months after a fever, surgery, a baby or a hard stretch is very often telogen effluvium, and the usual course is recovery. Still, see a clinician or board-certified dermatologist if shedding lasts more than 6 months or your part seems to be widening. MedlinePlus also lists reasons to get checked that include hair loss in an unusual pattern, scalp pain, itching or scaling, fatigue, trouble tolerating cold, and acne or facial hair with irregular periods.</p>
<p>Questions to ask:</p>
<ul>
<li>Could something in the last 6 months explain this, including a medicine change?</li>
<li>Should we check my iron, ferritin and thyroid?</li>
<li>Is this telogen effluvium, pattern hair loss, or both?</li>
<li>If it lasts past 6 months, what would you look at next?</li>
</ul>
<p>More in the <a href="/hair/">Hair</a> hub, including <a href="/hair/hair-thinning-perimenopause/">hair thinning in perimenopause</a>.</p>""",
 [("Hughes EC, Syed HA, Saleh D. Telogen Effluvium. StatPearls, NCBI Bookshelf (updated May 1, 2024)", "https://www.ncbi.nlm.nih.gov/sites/books/NBK430848/"),
  ("Whiting DA. Chronic telogen effluvium: increased scalp hair shedding in middle-aged women. J Am Acad Dermatol, 1996;35(6):899&ndash;906", "https://pubmed.ncbi.nlm.nih.gov/8959948/"),
  ("Asghar F, Shamim N, Farooque U, Sheikh H, Aqeel R. Telogen Effluvium: A Review of the Literature. Cureus, 2020;12(5):e8320", "https://www.cureus.com/articles/32514-telogen-effluvium-a-review-of-the-literature.pdf"),
  ("Rebora A. Proposing a Simpler Classification of Telogen Effluvium. Skin Appendage Disord, 2016;2:35&ndash;38", "https://europepmc.org/api/getPdf?pmcid=PMC5096129"),
  ("MedlinePlus Medical Encyclopedia. Hair loss (reviewed June 3, 2025)", "https://medlineplus.gov/ency/article/003246.htm"),
  ("MedlinePlus Medical Encyclopedia. Female pattern baldness (reviewed January 28, 2026)", "https://medlineplus.gov/ency/article/001173.htm")]),


article("/hair/biotin-for-hair/", "/hair/", "Hair",
 "Biotin for Hair: Does It Work? Plus the Lab-Test Warning",
 "Biotin for hair: does it work, and the lab-test warning",
 "What the research shows about biotin for hair loss in women without a deficiency, how rare deficiency is, and why FDA warns biotin can skew lab tests.",
 "2026-11-21",
 "Biotin is the headline ingredient in many hair, skin and nail supplements. The evidence behind it is much thinner than the shelf space suggests, and there is one safety issue worth knowing about before your next blood test.",
 "For hair loss in people who aren&rsquo;t biotin deficient, there is no good evidence that biotin helps: a 2024 review found no studies showing a benefit in healthy people. <b>Deficiency is rare in people eating a normal diet, and high-dose biotin can cause falsely high or low results on some blood tests, including heart and thyroid tests, so tell your clinician and lab if you take it.</b>",
 "review",
 [("Best evidence", "A 2024 literature review (<i>J Clin Aesthet Dermatol</i>) that found only 3 studies of biotin alone for hair; a 2017 review of 18 case reports (<i>Skin Appendage Disorders</i>)"),
  ("Women included?", "Yes. The only placebo-controlled trial (1966) studied women with diffuse hair loss; another study was 112 women after weight-loss surgery"),
  ("Dose or protocol tested", "The 1966 trial tested 10 mg a day for 4 weeks against placebo; the weight-loss surgery study tested 1 mg a day"),
  ("Bottom line", "Biotin helps hair when there&rsquo;s a real deficiency or a rare condition. For everyone else, the evidence isn&rsquo;t there, and the lab-test interference is a real risk")],
 """<h2>What is biotin, and how much do you need?</h2>
<p>Biotin is a water-soluble B vitamin. Your body uses it to process fats, sugars and protein, according to the NIH Office of Dietary Supplements (ODS).</p>
<p>There isn&rsquo;t enough data to set a full recommended daily allowance, so experts set an &ldquo;adequate intake&rdquo; instead:</p>
<table>
<tr><th>Group</th><th>Adequate intake (per day)</th></tr>
<tr><td>Women 19 and older</td><td>30 mcg</td></tr>
<tr><td>Pregnancy</td><td>30 mcg</td></tr>
<tr><td>Breastfeeding</td><td>35 mcg</td></tr>
</table>
<p>Many foods contain some biotin. ODS lists a cooked whole egg at 10 mcg, 3 ounces of canned pink salmon at 5 mcg, a quarter cup of roasted sunflower seeds at 2.6 mcg and half a cup of cooked sweet potato at 2.4 mcg. There are no national US estimates of intake, but ODS says average intakes in other Western countries are about 35 to 70 mcg a day.</p>
<p><b>ODS notes that no upper limit has been set, because there&rsquo;s no human evidence that biotin is toxic at high intakes. The bigger concern with high doses is lab tests (see below).</b></p>

<h2>How common is biotin deficiency?</h2>
<p>ODS says severe biotin deficiency has never been reported in healthy people eating a normal mixed diet. When deficiency does happen, signs include thinning hair (which can progress to losing all body hair), a scaly red rash around body openings, and brittle nails.</p>
<p>Groups ODS lists as more likely to run low:</p>
<ul>
<li><b>People with biotinidase deficiency,</b> a rare inherited disorder. All US newborns are screened for it.</li>
<li><b>People with long-term heavy alcohol use,</b> which blocks absorption.</li>
<li><b>Pregnant women.</b> ODS says at least a third of pregnant women develop marginal deficiency.</li>
<li><b>People who eat raw egg whites often.</b> A protein in raw egg white (avidin) binds biotin; cooking breaks it down.</li>
</ul>
<p>ODS also cites a study of 264 people with epilepsy that linked at least a year of anti-seizure medicine to lower biotin levels. If you take one, ask your prescriber rather than changing anything yourself.</p>
<p>One study complicates the picture. The 2024 review in the <i>Journal of Clinical and Aesthetic Dermatology</i> reports that a 2016 study by Tr&uuml;eb found low serum biotin in 38% of 541 women with hair loss. But the same review notes that another study found no difference between 60 people with telogen effluvium and 20 controls, and that serum biotin levels are thought to be unreliable. <b>A low lab number isn&rsquo;t the same as proof that biotin is causing your shedding.</b></p>

<h2>Does biotin work for hair loss? What the studies show</h2>
<p>The 2024 review (Yelich and colleagues) searched PubMed for studies of biotin on its own for hair growth or quality, leaving out case reports and case series. Out of 330 search results, only 3 studies qualified:</p>
<table>
<tr><th>Study</th><th>Who</th><th>What was tested</th><th>What was found</th></tr>
<tr><td>Pawlowski, 1966</td><td>46 women with diffuse hair loss (28 biotin, 18 placebo)</td><td>10 mg a day vs placebo, 4 weeks, double-blind</td><td>No significant difference in hair growth</td></tr>
<tr><td>Aksac, 2021</td><td>60 people taking isotretinoin (an acne drug that can cause shedding); 30 also got biotin</td><td>10 mg a day vs no biotin; not blinded</td><td>A shift toward more hairs in the growing phase on scalp imaging with biotin</td></tr>
<tr><td>Sen, 2021</td><td>112 women with hair loss after sleeve gastrectomy</td><td>1 mg a day</td><td>23% of deficient and 38% of non-deficient women reported improvement; no significant difference between groups</td></tr>
</table>
<p><b>The review found no studies showing that biotin improves hair growth in healthy people.</b> The authors called the evidence low quality. The review reported no funding and no relevant conflicts of interest.</p>
<p>An earlier review in <i>Skin Appendage Disorders</i> (Patel and colleagues, 2017) found 18 reported cases of biotin use for hair and nail changes. In every case, the patient had an underlying condition, such as inherited biotin-processing disorders, a side effect of the seizure drug valproic acid, brittle nail syndrome or uncombable hair syndrome. The authors concluded there wasn&rsquo;t enough evidence to support biotin for healthy people.</p>
<p>ODS reaches the same place: claims for biotin for hair, skin and nails rest, at best, on a few case reports and small studies. For hair specifically, ODS describes case reports only in children with uncombable hair syndrome.</p>

<h2>The biotin lab-test warning: why it matters</h2>
<p>Some lab tests use biotin as part of how they work. When there&rsquo;s a lot of biotin in your blood, it can throw those tests off. <b>FDA says biotin can cause falsely high or falsely low results, depending on the test, which can lead to misdiagnosis.</b> FDA issued safety communications about this on November 28, 2017, and November 5, 2019.</p>
<ul>
<li><b>Heart tests:</b> FDA says it has continued to receive adverse event reports of falsely low troponin results (troponin is used to diagnose heart attacks). ODS reports that, according to FDA, a patient with a high biotin intake died after a falsely low troponin result.</li>
<li><b>Thyroid tests:</b> ODS describes case reports of results falsely pointing to Graves&rsquo; disease and severe hyperthyroidism in people taking 10 to 300 mg a day. Even a single 10 mg dose interfered with thyroid tests run within 24 hours.</li>
<li><b>Other tests:</b> In six healthy adults taking 10 mg a day for a week, some tests gave falsely low TSH (a thyroid test) and NT-proBNP (a heart-failure marker). ODS also lists vitamin D among the tests very high biotin intakes can affect.</li>
</ul>
<p>For scale, FDA&rsquo;s October 2020 guidance says the usual 30 mcg daily intake keeps blood biotin below 1 ng/mL, while intakes of up to 300 mg a day produce levels above 1,000 ng/mL. A milligram is 1,000 micrograms, so 10 mg is more than 300 times the adequate intake for adult women.</p>
<p>FDA&rsquo;s troponin page, current as of June 2022, lists 17 troponin tests subject to biotin interference and says some test makers have addressed it while others have not. ODS says FDA advises clinicians to ask patients about supplements that contain biotin. <b>Ask your clinician or lab whether and when to pause biotin before a test, and don&rsquo;t skip a test because of it.</b></p>

<h2>Biotin for hair: the honest bottom line</h2>
<ul>
<li><b>If you have a confirmed deficiency or one of the rare conditions above,</b> biotin can help, under your clinician&rsquo;s care.</li>
<li><b>If you don&rsquo;t,</b> there&rsquo;s no good evidence it grows hair, and the one placebo-controlled trial in women found no difference.</li>
<li><b>If you take it anyway,</b> list it on every intake form and tell whoever orders your bloodwork.</li>
</ul>
<p>Shedding usually has another cause worth finding. Common ones include <a href="/hair/telogen-effluvium/">telogen effluvium</a>, <a href="/hair/iron-ferritin-hair-loss/">low iron and ferritin</a>, <a href="/hair/thyroid-hair-loss/">thyroid problems</a> and female pattern hair loss, which has treatments with trial evidence (see <a href="/hair/minoxidil-for-women/">minoxidil for women</a>). For an overview, start with <a href="/hair/female-hair-loss-causes/">hair loss in women: causes and how to tell them apart</a>.</p>
<p>Questions to ask a clinician or board-certified dermatologist:</p>
<ul>
<li>What do you think is causing my hair loss?</li>
<li>Is there any reason to test my biotin level, or would other tests tell us more?</li>
<li>I take biotin (or a supplement that contains it). Could it affect my upcoming blood tests?</li>
<li>Do any of my medicines affect biotin or my hair?</li>
</ul>
<p>More in the <a href="/hair/">Hair</a> hub, including <a href="/hair/hair-thinning-perimenopause/">hair thinning in perimenopause</a>.</p>""",
 [("Yelich A, Jenkins H, Holt S, Miller R. Biotin for Hair Loss: Teasing Out the Evidence. J Clin Aesthet Dermatol, 2024;17(8):56&ndash;61", "https://pmc.ncbi.nlm.nih.gov/articles/PMC11324195/"),
  ("Patel DP, Swink SM, Castelo-Soccio L. A Review of the Use of Biotin for Hair Loss. Skin Appendage Disord, 2017;3(3):166&ndash;169", "https://pmc.ncbi.nlm.nih.gov/articles/PMC5582478/"),
  ("NIH Office of Dietary Supplements. Biotin: Fact Sheet for Health Professionals", "https://ods.od.nih.gov/factsheets/Biotin-HealthProfessional/"),
  ("FDA. Testing for Biotin Interference in In Vitro Diagnostic Devices: Guidance for Industry (October 2020)", "https://www.fda.gov/media/127915/download"),
  ("FDA. Biotin Interference with Troponin Lab Tests: Assays Subject to Biotin Interference (content current as of June 21, 2022)", "https://www.fda.gov/medical-devices/in-vitro-diagnostics/biotin-interference-troponin-lab-tests-assays-subject-biotin-interference")]),


article("/hair/thyroid-hair-loss/", "/hair/", "Hair",
 "Thyroid and Hair Loss in Women: Which Tests to Ask About",
 "Thyroid and hair loss: which tests to ask about",
 "How an underactive or overactive thyroid is linked to hair shedding in women, how common thyroid problems are, and which blood tests check for them.",
 "2026-11-21",
 "Thinning hair is one of the listed symptoms of an underactive thyroid, and thyroid problems are common in women in midlife. Here&rsquo;s what the official sources and research say, and what testing usually looks like.",
 "Yes, thyroid problems can be linked to hair loss in women. NIH lists dry, thinning hair as a symptom of an underactive thyroid (hypothyroidism), and a 2024 study of 500 women with sudden shedding found an underactive or overactive thyroid in 252 of them. <b>The usual first test is a TSH blood test, often followed by free T4 and other thyroid tests if the result is off. Symptoms alone can&rsquo;t diagnose it.</b>",
 "human-obs",
 [("Best evidence", "A 2024 retrospective study (<i>Medicine</i>) of 500 women with telogen effluvium, plus NIH and US Office on Women&rsquo;s Health guidance"),
  ("Women included?", "Yes. The study included only women 18 and older"),
  ("Dose or protocol tested", "Not a treatment study. Women had blood tests for TSH, free T4 and free T3"),
  ("Bottom line", "Thyroid problems are common in women and can show up as shedding. A blood test, not a symptom checklist, tells you whether your thyroid is involved")],
 """<h2>Can thyroid problems cause hair loss?</h2>
<p>Your thyroid is a small gland in your neck that makes hormones controlling how your body uses energy. It can make too little (hypothyroidism, or underactive thyroid) or too much (hyperthyroidism, or overactive thyroid).</p>
<p>The National Institute of Diabetes and Digestive and Kidney Diseases (NIDDK) lists &ldquo;dry, thinning hair&rdquo; among the symptoms of hypothyroidism, along with fatigue, weight gain, trouble tolerating cold, joint and muscle pain, dry skin, heavy or irregular periods, a slowed heart rate and depression. The US Office on Women&rsquo;s Health lists dry, thinning hair too.</p>
<p>NIDDK&rsquo;s hyperthyroidism page doesn&rsquo;t list hair changes. Its symptoms include weight loss despite a bigger appetite, a fast or irregular heartbeat, nervousness, trouble sleeping, shaky hands, sweating and frequent bowel movements.</p>
<p><b>Hypothyroidism develops slowly, so NIDDK says you may not notice symptoms for months or even years.</b></p>

<h2>How common is thyroid disease in women?</h2>
<ul>
<li><b>Underactive thyroid:</b> NIDDK says nearly 5 out of 100 Americans 12 and older have hypothyroidism, most with mild or few obvious symptoms. Women are much more likely than men to develop it, and it&rsquo;s more common after 60.</li>
<li><b>Overactive thyroid:</b> about 1 in 100 Americans 12 and older, more often women and people over 60.</li>
<li><b>Over a lifetime:</b> the Office on Women&rsquo;s Health says one in eight women will develop a thyroid problem. It says women are especially likely to develop thyroid disease right after pregnancy and after menopause.</li>
</ul>
<p>The same office notes that thyroid symptoms are sometimes mistaken for menopause symptoms. That matters in your 40s, when shedding, tiredness and period changes can all have more than one cause.</p>
<p>NIDDK names Hashimoto&rsquo;s disease, an autoimmune condition, as the most common cause of hypothyroidism, and Graves&rsquo; disease as the most common cause of hyperthyroidism.</p>

<h2>What one study of thyroid and hair loss found</h2>
<p>A 2024 study in the journal <i>Medicine</i> (Bin Dayel and colleagues) looked back at records from one dermatology clinic in Saudi Arabia from 2012 to 2022.</p>
<table>
<tr><th>Detail</th><th>What the study reported</th></tr>
<tr><td>Who</td><td>500 women 18 and older with telogen effluvium (sudden, diffuse shedding) who had thyroid blood tests</td></tr>
<tr><td>Design</td><td>Retrospective (a look back at existing records), single clinic</td></tr>
<tr><td>Thyroid results</td><td>248 normal, 150 underactive, 102 overactive</td></tr>
<tr><td>Severity</td><td>Women with an underactive thyroid had more severe hair loss on average; 34% had severe loss, vs 18% of women with normal thyroid tests and 20% with an overactive thyroid</td></tr>
</table>
<p>The authors concluded that thyroid problems, especially hypothyroidism, are a common cause of telogen effluvium, and that thyroid testing belongs in the workup. <b>The limits are real: this was one clinic, looking backward, with women who had already been sent for testing, so it can&rsquo;t tell you how likely thyroid disease is for any one woman with shedding.</b> The authors also note that hair-loss scoring was subjective.</p>
<p>Researchers think an underactive thyroid disrupts the hair growth cycle, holding more hairs in the resting phase, according to the study&rsquo;s discussion. How an overactive thyroid affects hair is not fully understood. For more on that resting-phase shedding, see <a href="/hair/telogen-effluvium/">telogen effluvium</a>.</p>

<h2>Thyroid tests for hair loss: what to ask about</h2>
<p>NIDDK is clear that a hypothyroidism diagnosis can&rsquo;t be based on symptoms alone. Doctors use a history, an exam, and blood tests. According to MedlinePlus (from the National Library of Medicine) and the Office on Women&rsquo;s Health:</p>
<table>
<tr><th>Test</th><th>What it measures</th></tr>
<tr><td>TSH (thyroid-stimulating hormone)</td><td>A hormone from the pituitary gland that tells the thyroid how much hormone to make. When thyroid hormone is low, TSH goes up; when it&rsquo;s high, TSH drops. Usually the first test</td></tr>
<tr><td>T4 (free or total)</td><td>The main thyroid hormone. Often ordered if TSH is abnormal</td></tr>
<tr><td>T3</td><td>Another thyroid hormone, sometimes checked too</td></tr>
<tr><td>Thyroid antibodies</td><td>Help check for autoimmune causes such as Hashimoto&rsquo;s or Graves&rsquo; disease</td></tr>
</table>
<p>MedlinePlus notes that TSH alone can&rsquo;t show what is causing a thyroid problem, and that pregnancy, serious illness and older age can shift results. Ask before your blood draw whether you need to stop any medicine, but don&rsquo;t stop one unless you&rsquo;re told to.</p>
<p><b>One easy-to-miss detail: high-dose biotin, common in hair supplements, can skew thyroid test results.</b> NIH&rsquo;s Office of Dietary Supplements describes cases where biotin made results falsely look like an overactive thyroid. Tell your clinician and lab if you take it; see <a href="/hair/biotin-for-hair/">biotin for hair</a>.</p>
<p>The Office on Women&rsquo;s Health says screening for thyroid disease isn&rsquo;t recommended for most women. Testing is about your symptoms and history, so describe the shedding, when it started and anything else you&rsquo;ve noticed.</p>

<h2>Will hair grow back after thyroid treatment?</h2>
<p>None of the official sources we checked give a timeline for hair recovery after thyroid treatment, and the 2024 study didn&rsquo;t follow women after treatment. What is clear is that a thyroid problem is a cause to treat directly. The label for over-the-counter minoxidil for women says it won&rsquo;t help hair loss related to hypothyroidism.</p>
<p>Thyroid treatment is a decision for you and your clinician. Don&rsquo;t start, stop or change a thyroid medicine based on your hair.</p>

<h2>What this means for you</h2>
<ul>
<li><b>Thinning hair plus tiredness, feeling cold, weight or period changes</b> is worth raising with your clinician, especially if thyroid problems run in your family.</li>
<li><b>Thyroid isn&rsquo;t the only lab cause.</b> MedlinePlus says clinicians check for thyroid disease and iron deficiency when assessing female pattern hair loss; see <a href="/hair/iron-ferritin-hair-loss/">iron, ferritin and hair loss</a>.</li>
<li><b>Hair loss often has more than one cause in midlife.</b> Start with <a href="/hair/female-hair-loss-causes/">hair loss in women: causes and how to tell them apart</a>.</li>
</ul>
<p>Questions to ask your clinician or a board-certified dermatologist:</p>
<ul>
<li>Should my thyroid be checked, and which tests will you order?</li>
<li>If my TSH is normal, do I need any other thyroid tests?</li>
<li>Could any supplement I take, like biotin, affect the results?</li>
<li>What else could be causing my shedding?</li>
</ul>
<p>More in the <a href="/hair/">Hair</a> hub, including <a href="/hair/hair-thinning-perimenopause/">hair thinning in perimenopause</a>.</p>""",
 [("Bin Dayel S, Hussein RS, Atia T, Abahussein O, Al Yahya RS, Elsayed SH. Is thyroid dysfunction a common cause of telogen effluvium?: A retrospective study. Medicine (Baltimore), 2024;103(1):e36803", "https://pmc.ncbi.nlm.nih.gov/articles/PMC10766245/"),
  ("NIDDK. Hypothyroidism (Underactive Thyroid) (reviewed March 2021)", "https://www.niddk.nih.gov/health-information/endocrine-diseases/hypothyroidism"),
  ("NIDDK. Hyperthyroidism (Overactive Thyroid) (reviewed August 2021)", "https://www.niddk.nih.gov/health-information/endocrine-diseases/hyperthyroidism"),
  ("US Office on Women&rsquo;s Health. Thyroid disease", "https://womenshealth.gov/a-z-topics/thyroid-disease"),
  ("MedlinePlus Medical Tests. TSH (Thyroid-stimulating hormone) Test", "https://medlineplus.gov/lab-tests/tsh-thyroid-stimulating-hormone-test/"),
  ("NIH Office of Dietary Supplements. Biotin: Fact Sheet for Health Professionals", "https://ods.od.nih.gov/factsheets/Biotin-HealthProfessional/"),
  ("DailyMed (National Library of Medicine). Label: Minoxidil 5% (for women) topical foam", "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=dbda95f2-11a8-4b2f-af45-b791342fff70"),
  ("MedlinePlus Medical Encyclopedia. Female pattern baldness (reviewed January 28, 2026)", "https://medlineplus.gov/ency/article/001173.htm")]),


article("/hair/hair-thinning-perimenopause/", "/hair/", "Hair",
 "Hair Thinning in Perimenopause: Causes and What Helps",
 "Hair thinning in perimenopause: causes and what helps",
 "Why hair often thins around menopause, the medical causes to rule out, and what the evidence says about minoxidil, spironolactone, PRP and supplements.",
 "2026-11-21",
 "A wider part, a see-through crown, more hair in the brush. Hair changes are common in the years around menopause. Here&rsquo;s what the research says is going on and which options have evidence behind them.",
 "Hair thinning in perimenopause is often female pattern hair loss, which a 2022 dermatology review says commonly shows up around menopause, when falling estrogen is thought to play a part. <b>Thyroid disease and low iron are worth ruling out, and topical minoxidil is the only FDA-approved medicine for female pattern hair loss.</b> Evidence for other options is thinner.",
 "review",
 [("Best evidence", "A 2022 review on menopause and hair (<i>Clinical and Experimental Dermatology</i>); FDA-approved labeling for topical minoxidil; 2023 reviews of spironolactone"),
  ("Women included?", "Yes. The reviews focus on women; the spironolactone reviews pooled studies of mostly or only women"),
  ("Dose or protocol tested", "Over-the-counter minoxidil 5% foam for women is labeled for once-daily use on the scalp"),
  ("Bottom line", "Find the cause first. Minoxidil has the strongest evidence; spironolactone, PRP and lasers have some; HRT and most supplements lack good evidence for hair")],
 """<h2>Why does hair thin in perimenopause?</h2>
<p>Perimenopause is the run-up to menopause, when ovulation and periods become irregular and hot flashes may start. Menopause usually happens between 45 and 55, according to a 2022 review by Kamp and colleagues in <i>Clinical and Experimental Dermatology</i>.</p>
<p>Estrogen is thought to keep hairs in their growing phase longer. As estrogen falls, the review says, studies have found a smaller share of growing hairs in postmenopausal women, more over the front and top of the scalp than the back. Androgens (hormones such as testosterone) can hold back scalp follicles, but the review says falling estrogen is thought to be the bigger factor in women. <b>Most women with this kind of thinning have normal androgen levels.</b> Genes matter too.</p>
<p>MedlinePlus adds that hair naturally grows more slowly with age, and strands become finer and lighter. Nearly everyone has some hair loss with aging.</p>

<h2>Female pattern hair loss vs telogen effluvium</h2>
<p>Two kinds of hair loss are most common in midlife, and they behave differently:</p>
<table>
<tr><th></th><th>Female pattern hair loss</th><th>Telogen effluvium</th></tr>
<tr><td>What you notice</td><td>Gradual thinning on the top and crown, often starting as a widening part; the front hairline usually stays</td><td>Diffuse shedding all over the scalp, for example after childbirth</td></tr>
<tr><td>What&rsquo;s happening</td><td>Follicles slowly shrink and make finer, shorter hairs</td><td>More hairs than usual move into the resting phase and fall out</td></tr>
<tr><td>Course</td><td>Ongoing; MedlinePlus says untreated loss is permanent but rarely leads to near-total baldness</td><td>Depends on the trigger; see our telogen effluvium guide</td></tr>
</table>
<p>The two can overlap. Read more in <a href="/hair/telogen-effluvium/">telogen effluvium</a> and <a href="/hair/female-hair-loss-causes/">hair loss in women: causes and how to tell them apart</a>.</p>
<p>The Kamp review also flags frontal fibrosing alopecia, a scarring condition linked to the perimenopausal years that causes the hairline at the front and temples to recede and can affect the eyebrows. <b>Because it causes scarring, a receding front hairline is worth showing to a dermatologist promptly.</b></p>

<h2>Medical causes worth ruling out</h2>
<p>MedlinePlus says a clinician diagnosing female pattern hair loss checks for other causes, such as thyroid disease or iron deficiency, and for signs of too much androgen: unusual hair growth, period changes or new acne. The Kamp review adds that hormone tests are sometimes warranted when those signs are present, but that testing usually isn&rsquo;t needed unless hair loss is severe or fast.</p>
<ul>
<li><b>Thyroid:</b> an underactive thyroid lists dry, thinning hair among its symptoms, and the US Office on Women&rsquo;s Health says thyroid disease is more likely after menopause. See <a href="/hair/thyroid-hair-loss/">thyroid and hair loss</a>.</li>
<li><b>Iron:</b> MedlinePlus lists heavy menstrual bleeding among possible factors in female pattern hair loss, and iron deficiency among the causes to check. See <a href="/hair/iron-ferritin-hair-loss/">iron, ferritin and hair loss</a>.</li>
<li><b>Medicines:</b> MedlinePlus names some medicines, including estrogen-containing birth control pills, among possible contributors. Don&rsquo;t stop any medicine on your own; ask your prescriber.</li>
</ul>

<h2>What helps hair thinning in perimenopause?</h2>
<table>
<tr><th>Option</th><th>Status</th><th>What the sources say</th></tr>
<tr><td>Topical minoxidil</td><td>FDA-approved, over the counter</td><td>MedlinePlus says it may help hair grow in about 1 in 4 or 5 women and may slow or stop loss in most. The label says results may take 3 to 6 months, shedding can rise for up to 2 weeks at first, and regrown hair is likely lost within 3 to 4 months of stopping</td></tr>
<tr><td>Spironolactone (oral)</td><td>Prescription; not FDA-approved for hair loss</td><td>A 2023 meta-analysis of 5 studies (413 patients) found 56.6% improved overall, with higher rates when combined with minoxidil; the author called the evidence limited. See <a href="/hair/spironolactone-hair-loss-women/">spironolactone for hair loss</a></td></tr>
<tr><td>Oral minoxidil</td><td>Prescription; not FDA-approved for hair loss</td><td>Listed in the Kamp review as an option, with caution for people with heart conditions. See <a href="/hair/minoxidil-for-women/">minoxidil for women</a></td></tr>
<tr><td>PRP and low-level laser</td><td>In-office or device-based</td><td>MedlinePlus lists both as options if minoxidil doesn&rsquo;t work; the Kamp review says more research is needed on PRP outcomes</td></tr>
<tr><td>Hair transplant</td><td>Surgery</td><td>MedlinePlus says results can be excellent for women who don&rsquo;t respond to medicine, but it can take many sessions and carries some scarring and infection risk</td></tr>
</table>
<p>Finasteride and dutasteride are also discussed in the Kamp review. They are prescription drugs not approved for women&rsquo;s hair loss, and the review notes contraception is advised for premenopausal women taking dutasteride.</p>
<p><b>Minoxidil works only while you use it, and none of these options is a quick fix.</b> MedlinePlus also notes that if you&rsquo;re comfortable with your appearance, you don&rsquo;t need treatment, and that styling changes and hairpieces are often the safest and least expensive route.</p>

<h2>Does HRT help with menopausal hair thinning?</h2>
<p>Not on current evidence. The Kamp review says there is insufficient evidence for hormone therapy as a treatment for female pattern hair loss, and that surprisingly little research has looked at hormone therapy and hair. Decisions about hormone therapy are about your overall health, made with your clinician, not about your hair alone.</p>

<h2>Biotin and &ldquo;hair vitamins&rdquo;</h2>
<p>NIH&rsquo;s Office of Dietary Supplements says claims for biotin for hair rest, at best, on a few case reports and small studies, and a 2024 review found no studies showing benefit in healthy people. The Kamp review says more research is needed on supplements for hair. <b>High-dose biotin can also cause falsely high or low results on some lab tests, including thyroid and heart tests, FDA warns.</b> Details are in <a href="/hair/biotin-for-hair/">biotin for hair</a>.</p>

<h2>The honest bottom line</h2>
<ul>
<li><b>Thinning around menopause is common</b> and is usually female pattern hair loss, sometimes mixed with shedding from another cause.</li>
<li><b>Get the cause checked</b>, especially thyroid and iron, before spending on products.</li>
<li><b>See a dermatologist promptly</b> for sudden or patchy loss, a receding front hairline, scalp pain, itching or redness.</li>
</ul>
<p>Questions to ask a board-certified dermatologist:</p>
<ul>
<li>Is this female pattern hair loss, shedding, or both?</li>
<li>Which blood tests make sense for me?</li>
<li>Is topical minoxidil a reasonable first step, and how long should I give it?</li>
<li>Are prescription options right for my health history?</li>
</ul>
<p>More in the <a href="/hair/">Hair</a> hub.</p>""",
 [("Kamp E, Ashraf M, Musbahi E, DeGiovanni C. Menopause, skin and common dermatoses. Part 1: hair disorders. Clin Exp Dermatol, 2022;47(12):2110&ndash;2116", "https://pmc.ncbi.nlm.nih.gov/articles/PMC10092469/"),
  ("Aleissa M. The Efficacy and Safety of Oral Spironolactone in the Treatment of Female Pattern Hair Loss: A Systematic Review and Meta-Analysis. Cureus, 2023;15(8):e43559", "https://assets.cureus.com/uploads/review_article/pdf/166490/20230915-13630-10cfn21.pdf"),
  ("DailyMed (National Library of Medicine). Label: Minoxidil 5% (for women) topical foam", "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=dbda95f2-11a8-4b2f-af45-b791342fff70"),
  ("MedlinePlus Medical Encyclopedia. Female pattern baldness (reviewed January 28, 2026)", "https://medlineplus.gov/ency/article/001173.htm"),
  ("MedlinePlus Medical Encyclopedia. Aging changes in hair and nails (reviewed July 15, 2024)", "https://medlineplus.gov/ency/article/004005.htm"),
  ("US Office on Women&rsquo;s Health. Thyroid disease", "https://womenshealth.gov/a-z-topics/thyroid-disease"),
  ("NIDDK. Hypothyroidism (Underactive Thyroid)", "https://www.niddk.nih.gov/health-information/endocrine-diseases/hypothyroidism"),
  ("NIH Office of Dietary Supplements. Biotin: Fact Sheet for Health Professionals", "https://ods.od.nih.gov/factsheets/Biotin-HealthProfessional/"),
  ("Yelich A, Jenkins H, Holt S, Miller R. Biotin for Hair Loss: Teasing Out the Evidence. J Clin Aesthet Dermatol, 2024;17(8):56&ndash;61", "https://pmc.ncbi.nlm.nih.gov/articles/PMC11324195/"),
  ("FDA. Testing for Biotin Interference in In Vitro Diagnostic Devices: Guidance for Industry (October 2020)", "https://www.fda.gov/media/127915/download")]),


article("/hair/spironolactone-hair-loss-women/", "/hair/", "Hair",
 "Spironolactone for Hair Loss in Women: The Evidence",
 "Spironolactone for female pattern hair loss: the evidence",
 "Spironolactone is used off-label for female pattern hair loss. What reviews of the studies found, side effects, and why it isn&rsquo;t used in pregnancy.",
 "2026-11-21",
 "Spironolactone is a decades-old blood pressure and heart medicine that dermatologists sometimes prescribe for thinning hair in women. Here&rsquo;s what the studies show, what they don&rsquo;t, and what to ask before trying it.",
 "Spironolactone is not FDA-approved for hair loss, but it&rsquo;s prescribed off-label for female pattern hair loss as an anti-androgen. A 2023 meta-analysis of 5 studies found that 56.6% of patients improved, more when it was combined with minoxidil. <b>The evidence is mostly small, non-randomized studies, and the drug&rsquo;s label says to avoid it in pregnancy because of possible effects on a male fetus.</b>",
 "review",
 [("Best evidence", "A 2023 meta-analysis (<i>Cureus</i>, 5 studies, 413 patients) and a 2023 systematic review (<i>Clinical, Cosmetic and Investigational Dermatology</i>, 7 studies, 618 patients)"),
  ("Women included?", "Yes. The oral studies in the 2023 systematic review were all in women (295)"),
  ("Dose or protocol tested", "Oral doses from 25 mg to 200 mg a day, mostly 80 to 110 mg, usually for 6 months to over a year"),
  ("Bottom line", "Promising but low-quality evidence, with only one or two randomized trials. A prescription decision that needs a clinician and some monitoring")],
 """<h2>What is spironolactone, and why is it used for hair loss?</h2>
<p>Spironolactone was first approved in the US in 1960. Its FDA-approved uses, per the current label, are certain kinds of heart failure, high blood pressure, fluid buildup from liver or kidney disease, and a hormone condition called primary hyperaldosteronism. Hair loss is not on the list.</p>
<p>Dermatologists use it &ldquo;off-label&rdquo; (for a use the FDA hasn&rsquo;t approved) because it acts as an anti-androgen. Androgens are hormones such as testosterone that can hold back scalp hair follicles, according to a 2022 dermatology review by Kamp and colleagues. MedlinePlus lists it among the options when topical minoxidil, the only FDA-approved medicine for female pattern hair loss, doesn&rsquo;t work. The Kamp review lists it among treatments for menopause-related hair loss.</p>
<p><b>Off-label prescribing is legal and common, but it means the drug hasn&rsquo;t gone through FDA review for this use.</b></p>

<h2>Spironolactone for female pattern hair loss: what the studies show</h2>
<p>Two 2023 reviews pulled the research together:</p>
<table>
<tr><th>Review</th><th>What was included</th><th>Main findings</th></tr>
<tr><td>Aleissa, <i>Cureus</i> (systematic review and meta-analysis)</td><td>5 studies of oral spironolactone for female pattern hair loss, 413 patients; only one was a randomized trial</td><td>56.6% improved overall; 65.8% when combined with minoxidil vs 43.2% on spironolactone alone. Results varied a lot between studies</td></tr>
<tr><td>Wang and colleagues, <i>Clinical, Cosmetic and Investigational Dermatology</i> (systematic review)</td><td>7 studies of androgenetic alopecia, 618 patients (553 women); 5 oral studies, all in women; 2 randomized trials</td><td>81% (158 of 195) reported better hair growth in four oral studies; combination with minoxidil did better than single treatment in the three studies that compared them</td></tr>
</table>
<p>A few individual studies give a sense of the details:</p>
<ul>
<li><b>Sinclair, 2005:</b> 80 women followed for an average of 16 months on oral anti-androgens; 80% had no further progression or improved.</li>
<li><b>Famenini, 2015:</b> 19 women; 74.3% reported improvement or stabilization.</li>
<li><b>Sinclair, 2018:</b> 100 women on low-dose spironolactone plus low-dose oral minoxidil for 12 months; shedding and density scores improved over time. There was no comparison group.</li>
<li><b>Liang, 2022:</b> the one randomized trial in the meta-analysis, 115 patients over 24 weeks. Topical minoxidil plus microneedling did better than minoxidil plus oral spironolactone or minoxidil alone.</li>
</ul>
<p>Doses in the studies ranged from 25 to 200 mg a day, most between 80 and 110 mg. These are the doses that were tested, not a recommendation; dosing is for your clinician to decide.</p>
<p><b>Both reviews call for better trials.</b> The meta-analysis author noted the small number of patients, the mix of study designs and doses, and wide variation in results. The systematic review authors couldn&rsquo;t pool results because studies measured hair differently. The meta-analysis reported no funding; the systematic review was funded by a national science grant in China, and both reported no conflicts of interest.</p>

<h2>Side effects of spironolactone</h2>
<p>In the hair-loss studies, side effects were usually mild. In the systematic review&rsquo;s safety data from 216 people on oral spironolactone:</p>
<table>
<tr><th>Side effect</th><th>How often</th></tr>
<tr><td>Menstrual changes</td><td>7.9%</td></tr>
<tr><td>Dizziness or headache</td><td>6.5%</td></tr>
<tr><td>Unwanted facial hair</td><td>4.1%</td></tr>
<tr><td>High potassium</td><td>0.9% (2 people)</td></tr>
<tr><td>Stopped because of side effects</td><td>3.2%</td></tr>
</table>
<p>The authors noted side effects were more common at 80 to 110 mg a day than at 25 mg. In one randomized trial in the meta-analysis, 40.5% of patients reported menstrual changes, so rates differ a lot between studies.</p>
<p>The FDA label lists warnings for <b>high potassium</b>, low blood pressure, worsening kidney function and other electrolyte changes, and says potassium should be checked within a week of starting and regularly after. It lists irregular or missed periods, postmenopausal bleeding, and breast and nipple pain among reproductive side effects. MedlinePlus advises avoiding potassium-containing salt substitutes. Drugs that raise potassium, including potassium supplements, some blood pressure medicines (ACE inhibitors and ARBs), NSAID pain relievers and trimethoprim, can interact.</p>
<p>MedlinePlus also notes that spironolactone has caused tumors in laboratory animals. That is an animal finding; ask your prescriber what it means for you.</p>

<h2>Why spironolactone isn&rsquo;t used in pregnancy</h2>
<p>The FDA label says that, based on animal studies, spironolactone may affect how a male fetus develops sexually. In rats given high doses late in pregnancy, male fetuses showed feminization. The label says to avoid spironolactone in pregnancy or advise of the potential risk to a male fetus. <b>If you could become pregnant, ask your clinician about this before starting.</b></p>

<h2>What this means for you</h2>
<ul>
<li><b>Spironolactone has some evidence for female pattern hair loss,</b> especially alongside minoxidil, but the studies are small and mostly not randomized.</li>
<li><b>It&rsquo;s a prescription drug with real monitoring needs,</b> especially for potassium and kidney function.</li>
<li><b>Get the cause confirmed first.</b> Shedding from <a href="/hair/telogen-effluvium/">telogen effluvium</a>, <a href="/hair/thyroid-hair-loss/">thyroid problems</a> or <a href="/hair/iron-ferritin-hair-loss/">low iron</a> needs a different approach. See <a href="/hair/female-hair-loss-causes/">hair loss in women: causes</a>.</li>
</ul>
<p>Questions to ask a board-certified dermatologist:</p>
<ul>
<li>Is my hair loss female pattern hair loss, and how sure are you?</li>
<li>Should I try <a href="/hair/minoxidil-for-women/">topical minoxidil</a> first, or combine treatments?</li>
<li>Do my other medicines or health conditions make spironolactone risky for me?</li>
<li>Which blood tests will I need, and how often?</li>
<li>What should I do about contraception while taking it?</li>
<li>How long before we judge whether it&rsquo;s working?</li>
</ul>
<p>More in the <a href="/hair/">Hair</a> hub, including <a href="/hair/hair-thinning-perimenopause/">hair thinning in perimenopause</a>.</p>""",
 [("Aleissa M. The Efficacy and Safety of Oral Spironolactone in the Treatment of Female Pattern Hair Loss: A Systematic Review and Meta-Analysis. Cureus, 2023;15(8):e43559", "https://assets.cureus.com/uploads/review_article/pdf/166490/20230915-13630-10cfn21.pdf"),
  ("Wang C, Du Y, Bi L, Lin X, Zhao M, Fan W. The Efficacy and Safety of Oral and Topical Spironolactone in Androgenetic Alopecia Treatment: A Systematic Review. Clin Cosmet Investig Dermatol, 2023;16:603&ndash;612", "https://www.dovepress.com/the-efficacy-and-safety-of-oral-and-topical-spironolactone-in-androgen-peer-reviewed-fulltext-article-CCID"),
  ("DailyMed (National Library of Medicine). Aldactone (spironolactone) tablets prescribing information (revised November 2025)", "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=0fed2822-3a03-4b64-9857-c682fcd462bc"),
  ("MedlinePlus Drug Information. Spironolactone", "https://medlineplus.gov/druginfo/meds/a682627.html"),
  ("MedlinePlus Medical Encyclopedia. Female pattern baldness (reviewed January 28, 2026)", "https://medlineplus.gov/ency/article/001173.htm"),
  ("Kamp E, Ashraf M, Musbahi E, DeGiovanni C. Menopause, skin and common dermatoses. Part 1: hair disorders. Clin Exp Dermatol, 2022;47(12):2110&ndash;2116", "https://pmc.ncbi.nlm.nih.gov/articles/PMC10092469/")]),


article("/hair/pumpkin-seed-oil-hair/", "/hair/", "Hair",
 "Pumpkin Seed Oil for Hair: What the Study Showed",
 "Pumpkin seed oil for hair: what the study showed",
 "Does pumpkin seed oil help hair loss? The placebo-controlled trial studied men taking a capsule. What it found, its limits, and the evidence in women.",
 "2026-11-22",
 "Pumpkin seed oil shows up on almost every list of natural hair-loss remedies. Most of those lists lean on one placebo-controlled trial. Here&rsquo;s who was in it, what they actually took, and what it can and can&rsquo;t tell a woman whose hair is thinning.",
 "One 2014 randomized, placebo-controlled trial found that men with pattern hair loss who took a capsule containing pumpkin seed oil for 24 weeks had more hair than men on placebo. <b>The trial studied only men, was funded by the capsule&rsquo;s maker, and has not been repeated; the only trial in women had no placebo group.</b>",
 "human-trial",
 [("Best evidence", "One randomized, double-blind, placebo-controlled trial of 76 men with mild to moderate pattern hair loss (2014)"),
  ("Women included?", "No. The one trial in women (60 women, 2021) compared topical pumpkin seed oil with minoxidil foam, with no placebo group"),
  ("Protocol tested", "A capsule supplement providing 400 mg of pumpkin seed oil a day for 24 weeks (men); topical pumpkin seed oil vs. 5% minoxidil foam for 3 months (women)"),
  ("Bottom line", "An encouraging but small, single, industry-funded result in men. Not enough to know whether pumpkin seed oil helps women&rsquo;s hair loss")],
 """<h2>Where the pumpkin seed oil for hair claim comes from</h2>
<p>The study most often cited is a trial by Cho and colleagues, published in 2014 in the journal <i>Evidence-Based Complementary and Alternative Medicine</i>. The authors described it as the first randomized, double-blind, placebo-controlled trial of pumpkin seed oil in men with pattern hair loss (androgenetic alopecia, the most common type of thinning in both men and women).</p>
<p>A 2026 systematic review of oral hair supplements in the <i>Journal of Cosmetic Dermatology</i> describes the same trial when it discusses pumpkin seed oil. <b>For oral pumpkin seed oil on its own, this is still the key human study.</b></p>

<h2>What the pumpkin seed oil trial tested</h2>
<ul>
<li><b>Who:</b> 76 men aged 20 to 65, recruited at a hospital in Korea, (average age about 46) with mild to moderate pattern hair loss. No women were included.</li>
<li><b>Design:</b> randomized and double-blind. 37 men took the active capsules and 39 took a look-alike placebo. 12 dropped out (5 and 7).</li>
<li><b>What they took:</b> a branded capsule supplement with 100 mg of pumpkin seed oil per capsule, 4 capsules a day, for a total of 400 mg a day. The paper doesn&rsquo;t list any other ingredients in the capsule, so we can&rsquo;t say whether it contained anything besides pumpkin seed oil. That&rsquo;s the amount tested, not a recommendation; talk to your clinician.</li>
<li><b>How long:</b> 24 weeks, with checks at 12 and 24 weeks.</li>
<li><b>What was measured:</b> blinded ratings of standardized scalp photos, the men&rsquo;s own ratings of improvement and satisfaction, and hair count and thickness at the thinnest spot using magnified scalp imaging.</li>
</ul>

<h2>What did the pumpkin seed oil trial find?</h2>
<ul>
<li><b>Hair count:</b> up 40% from the start in the pumpkin seed oil group at 24 weeks, compared with 10% in the placebo group.</li>
<li><b>Photo ratings:</b> at 24 weeks, 17 of 37 men on pumpkin seed oil were rated slightly or moderately improved, compared with 3 of 39 on placebo. 1 man on pumpkin seed oil and 11 on placebo were rated worse. About half of each group looked unchanged.</li>
<li><b>Self-ratings:</b> no difference between groups at 12 weeks. By 24 weeks, the pumpkin seed oil group rated their improvement and satisfaction higher, though the average scores were modest (about 3.4 out of 10 vs. about 2.1 for improvement).</li>
<li><b>Hair thickness:</b> no difference between groups.</li>
</ul>
<p><b>So the main gains were in hair count and photo ratings, not in thicker hair.</b></p>

<h2>The limits of one small trial</h2>
<ul>
<li><b>Only men.</b> Results in men may not carry over to female pattern hair loss.</li>
<li><b>Industry funding.</b> The study was paid for by the company that supplied the capsules, and that company also held the randomization codes. The authors declared no conflict of interest.</li>
<li><b>Not repeated.</b> The authors themselves called it a first-stage study and said it needs to be replicated.</li>
<li><b>Mechanism unknown.</b> The team didn&rsquo;t measure DHT, the hormone involved in pattern hair loss, so they said they couldn&rsquo;t explain how the oil might work.</li>
<li><b>Small.</b> 76 men over 6 months is a short, small test for a condition that develops over years.</li>
</ul>
<p>The 2026 review of oral hair supplements noted that several of the trials it looked at were funded or supported by supplement makers, and concluded that more rigorous, independent research is needed. A 2026 network meta-analysis in <i>Frontiers in Nutrition</i>, which compared 16 supplements across 19 trials, listed pumpkin seed oil among the supplements that improved hair density compared with placebo, ranking it fifth of 10 for that outcome.</p>

<h2>Is there any pumpkin seed oil study in women?</h2>
<p>One, and it tested the oil on the scalp, not as a supplement. A 2024 review in <i>Clinical, Cosmetic and Investigational Dermatology</i> summarizes a 2021 randomized trial by Ibrahim and colleagues in the <i>Journal of Cosmetic Dermatology</i>:</p>
<ul>
<li><b>Who:</b> 60 women with female pattern hair loss, 30 per group.</li>
<li><b>Design:</b> randomized and comparative. One group put 1 mL of pumpkin seed oil on the scalp; the other used 1 mL of 5% minoxidil foam (see <a href="/hair/minoxidil-for-women/">our minoxidil guide</a>). There was no placebo group.</li>
<li><b>How long:</b> 3 months.</li>
<li><b>Found:</b> a hair-shaft measure the review calls &ldquo;hair shaft diversity&rdquo; improved in both groups (from about 30.5% to 24.0% with pumpkin seed oil and from 31.5% to 21.3% with minoxidil). The review doesn&rsquo;t report a head-to-head comparison.</li>
</ul>
<p><b>Without a placebo group, this study can&rsquo;t show how much of the change came from the oil itself.</b> We could not open the full trial report in this run, so details beyond the review&rsquo;s summary aren&rsquo;t included here.</p>
<p>A 2025 review in the <i>International Journal of Trichology</i> also describes a study of a topical serum of pumpkin seed oil in tiny lipid carriers (niosomes), in 42 people over 8 weeks, which reported changes in hair shedding and in the share of growing hairs. The review graded it as non-randomized, lower-level evidence, and the sex of participants wasn&rsquo;t given.</p>

<h2>Lab and animal studies: an idea, not proof</h2>
<p>The usual explanation for why pumpkin seed oil might help is that its plant sterols, especially beta-sitosterol, block 5-alpha-reductase, the enzyme that makes DHT. Reviews present this as a possibility. In one mouse study described in the 2024 review, mice given testosterone to cause hair loss grew more hair with 10% pumpkin seed oil, as they did with 2% minoxidil. <b>Mouse results don&rsquo;t tell us what the oil does for women.</b></p>

<h2>Pumpkin seed oil safety: what the trial reported</h2>
<p>In the 2014 trial, side effects were few and similar between groups: whole-body itching in 1 man on pumpkin seed oil and 1 on placebo, and mild stomach discomfort in 1 man on pumpkin seed oil. The authors reported no changes in average liver or kidney blood tests in the pumpkin seed oil group; at 24 weeks, 1 man on pumpkin seed oil and 2 on placebo had a raised liver-enzyme reading. That&rsquo;s 24 weeks of data in 37 men, so it can&rsquo;t speak to longer use, women, pregnancy or interactions with medications. Talk to your clinician before starting any supplement.</p>

<h2>Pumpkin seed oil studies at a glance</h2>
<table>
<tr><th>Study</th><th>Who</th><th>Design</th><th>Length</th><th>Result</th></tr>
<tr><td>Cho et al., 2014</td><td>76 men, 20&ndash;65, pattern hair loss</td><td>Randomized, double-blind, placebo-controlled; 400 mg/day oral pumpkin seed oil capsule; maker-funded</td><td>24 weeks</td><td>Hair count +40% vs. +10% placebo; no change in thickness</td></tr>
<tr><td>Ibrahim et al., 2021 (as summarized in a 2024 review)</td><td>60 women, female pattern hair loss</td><td>Randomized; topical pumpkin seed oil vs. 5% minoxidil foam; no placebo</td><td>3 months</td><td>A hair-shaft measure improved in both groups</td></tr>
<tr><td>Niosome serum study (as summarized in a 2025 review)</td><td>42 people</td><td>Non-randomized; topical serum</td><td>8 weeks</td><td>Changes in shedding reported; no control group described</td></tr>
<tr><td>Mouse study (as summarized in a 2024 review)</td><td>Mice with testosterone-induced hair loss</td><td>10% pumpkin seed oil vs. 2% minoxidil</td><td>&mdash;</td><td>More hair growth; animal result only</td></tr>
</table>

<h2>What this means for you</h2>
<p>Pumpkin seed oil has one small placebo-controlled trial behind it, in men, paid for by the supplement&rsquo;s maker. The one trial in women had no placebo group. <b>For women, the evidence is too thin to say whether it helps.</b> It also doesn&rsquo;t replace finding out why your hair is thinning: low iron, thyroid problems and other medical causes need their own care. Start with our guide to <a href="/hair/female-hair-loss-causes/">the causes of hair loss in women</a> and our explainer on <a href="/hair/iron-ferritin-hair-loss/">iron, ferritin and hair loss</a>.</p>
<p>Questions to bring to a board-certified dermatologist:</p>
<ul>
<li>What type of hair loss do I have, and what&rsquo;s likely causing it?</li>
<li>Which treatments have FDA approval or trial evidence for my type? (See <a href="/hair/minoxidil-for-women/">minoxidil for women</a> and <a href="/hair/spironolactone-hair-loss-women/">spironolactone</a>.)</li>
<li>Could a supplement or scalp oil interact with my medications or irritate my skin?</li>
<li>How long should I give any treatment before judging whether it&rsquo;s working?</li>
</ul>
<p>More evidence checks on natural remedies are in our <a href="/hair/">Hair</a> hub, including <a href="/hair/rosemary-oil-hair-growth/">rosemary oil</a> and <a href="/hair/biotin-for-hair/">biotin</a>.</p>""",
 [("Cho YH, Lee SY, Jeong DW, et al. Effect of Pumpkin Seed Oil on Hair Growth in Men with Androgenetic Alopecia: A Randomized, Double-Blind, Placebo-Controlled Trial. Evid Based Complement Alternat Med, 2014;2014:549721", "https://pmc.ncbi.nlm.nih.gov/articles/PMC4017725/"),
  ("Alanazi R, et al. Evaluating the Effectiveness of Commercial Oral Supplements for Hair Growth: A Systematic Review and Meta-Analysis. J Cosmet Dermatol, 2026;25:e70817", "https://pmc.ncbi.nlm.nih.gov/articles/PMC13063204/"),
  ("Zhou L, Zhu W, Chen Y. Effects of dietary supplements on androgenetic alopecia: a systematic review and network meta-analysis. Front Nutr, 2026;12:1719711", "https://pmc.ncbi.nlm.nih.gov/articles/PMC12812558/"),
  ("Bin Rubaian NF, Alzamami HFA, Amir BA. An Overview of Commonly Used Natural Alternatives for the Treatment of Androgenetic Alopecia, with Special Emphasis on Rosemary Oil. Clin Cosmet Investig Dermatol, 2024;17:2495&ndash;2503", "https://pmc.ncbi.nlm.nih.gov/articles/PMC11549889/"),
  ("Bikash C. Topical Alternatives for Hair Loss: Beyond the Conventional. Int J Trichology, 2025;17(1):13&ndash;19", "https://pmc.ncbi.nlm.nih.gov/articles/PMC12251978/")]),


article("/fitness/zone-2-cardio-women/", "/fitness/", "Fitness",
 "Zone 2 Cardio for Women: What It Is and How Much",
 "Zone 2 cardio for women: what it is and how much",
 "What zone 2 cardio means, how to find it with the talk test, how much US guidelines call for, and what research says about mitochondria and the hype.",
 "2026-11-23",
 "&ldquo;Zone 2&rdquo; has become the cardio buzzword of the decade, sold as the best way to build your mitochondria and live longer. Here&rsquo;s what it actually means, how much aerobic exercise official guidelines call for, and where the research is more modest than the marketing.",
 "Zone 2 is steady, easy-to-moderate cardio, roughly a pace where you can still talk but not sing. US guidelines call for 150 to 300 minutes a week of moderate activity (or 75 to 150 of vigorous). <b>Steady cardio does build fitness and mitochondria, but reviews find no proof that zone 2 is the single best intensity; harder efforts and total amount matter too.</b>",
 "review",
 [("Best evidence", "A large systematic review and meta-regression of exercise training and muscle mitochondria (353 studies, 5,650 participants in its main models); a 2025 narrative review of zone 2 in <i>Sports Medicine</i>; US Physical Activity Guidelines (2018)"),
  ("Women included?", "Yes, though the share isn&rsquo;t clear. In the meta-regression, mitochondrial gains didn&rsquo;t differ by sex. A 2025 lab study of how to define zone 2 included 20 women among 50 cyclists"),
  ("Protocol tested", "Continuous endurance training compared with interval and sprint training, over weeks; zone 2 itself has no single agreed definition"),
  ("Bottom line", "Steady cardio is a solid way to meet the guidelines. It&rsquo;s not magic, and a mix of easy and harder work is also well supported")],
 """<h2>What is zone 2 cardio?</h2>
<p>Exercise physiologists split effort into &ldquo;zones&rdquo; from very easy to all-out. Zone 2 is the second-lowest: steady work just below the point where your body starts relying much more on fast, sugar-burning energy and lactate begins to build up. Scientists call that point the first lactate or ventilatory threshold.</p>
<p><b>There&rsquo;s no single agreed definition of zone 2.</b> A 2025 lab study in <i>Translational Sports Medicine</i> tested 50 experienced cyclists (30 men and 20 women, average age about 31) and compared several ways of setting zone 2: fixed blood-lactate values, the first ventilatory threshold, the intensity of peak fat burning, a share of peak oxygen use, and a common rule of 72% to 82% of maximum heart rate.</p>
<ul>
<li>The methods placed zone 2 at different intensities. On average, the 72% heart-rate cut-off and the point of peak fat burning sat well below the first ventilatory threshold.</li>
<li>On average, the 82% heart-rate cut-off landed at about the same power output as the ventilatory threshold.</li>
<li>Women&rsquo;s heart rate at peak fat burning sat at a higher share of their maximum than men&rsquo;s.</li>
</ul>
<p>The authors concluded that fixed percentages of maximum heart rate are simple but may not reflect what&rsquo;s happening in your muscles. The study was a one-time snapshot of fit cyclists on a bike, so it doesn&rsquo;t tell us what training at each zone does over time.</p>

<h2>How to find zone 2 without a lab: the talk test</h2>
<p>Lab tests measure lactate in your blood or the gases you breathe out. At home, the simplest tool is one the CDC already uses for moderate intensity:</p>
<table>
<tr><th>Check</th><th>Moderate intensity (close to what most people mean by zone 2)</th><th>Vigorous intensity</th></tr>
<tr><td>Talk test (CDC)</td><td>You can talk, but not sing</td><td>You can&rsquo;t say more than a few words without pausing for breath</td></tr>
<tr><td>Effort on a 0&ndash;10 scale (CDC)</td><td>5 or 6</td><td>Starts at 7 or 8</td></tr>
<tr><td>Examples (CDC and HHS)</td><td>Brisk walking, bicycling under 10 mph on flat ground, water aerobics, doubles tennis</td><td>Jogging or running, swimming laps, bicycling faster than 10 mph, jumping rope</td></tr>
</table>
<p>These are general guides, not a precise match for a lab-measured threshold. The CDC also notes that what feels vigorous for one person can be moderate for a fitter one, which is why effort and breathing are useful checks. More on what wearables can and can&rsquo;t measure lives in <a href="/health-trackers/">Health Trackers</a>.</p>

<h2>How much zone 2 cardio do women need?</h2>
<p>No official guideline uses the term zone 2. The US <i>Physical Activity Guidelines for Americans</i> (2nd edition, 2018, from HHS) give the numbers that matter for adults:</p>
<ul>
<li><b>Aerobic:</b> 150 to 300 minutes a week of moderate activity, or 75 to 150 minutes of vigorous activity, or a mix of the two.</li>
<li><b>Spread it out:</b> preferably across the week.</li>
<li><b>Muscle-strengthening:</b> moderate or harder work for all major muscle groups on 2 or more days a week.</li>
<li><b>Some is better than none,</b> and going beyond 300 minutes of moderate activity brings additional health benefits.</li>
</ul>
<p>The guidelines count brisk walking at 2.5 to 4 mph as moderate. They also dropped an old rule that activity had to come in bouts of at least 10 minutes, so shorter sessions count.</p>

<h2>Does zone 2 build mitochondria? What human studies show</h2>
<p>Mitochondria are the parts of your cells that use oxygen to make energy. The main zone 2 claim is that steady, easy cardio is the best way to grow more of them.</p>
<h3>The big picture from hundreds of studies</h3>
<p>A large systematic review and meta-regression pooled training studies in human muscle published up to February 2022. Its main mitochondrial analyses covered 353 studies and 5,650 people, from young to over 55, untrained to well-trained, healthy and with conditions such as heart or metabolic disease. It compared continuous endurance training (low to moderate intensity), high-intensity interval training and sprint interval training.</p>
<table>
<tr><th>Training type</th><th>Average total training time</th><th>Adjusted rise in mitochondrial markers</th></tr>
<tr><td>Continuous endurance (low to moderate)</td><td>About 39 hours</td><td>About 23%</td></tr>
<tr><td>High-intensity intervals</td><td>About 23 hours</td><td>About 27%</td></tr>
<tr><td>Sprint intervals</td><td>About 8 hours</td><td>About 27%</td></tr>
</table>
<ul>
<li>All three raised mitochondrial markers by similar amounts, but the harder types did it in less total time.</li>
<li>Bigger gains came with more volume and with higher intensity; the authors judged intensity multiplied by volume (training load) the best predictor.</li>
<li>People starting out less fit gained more.</li>
<li><b>The gains didn&rsquo;t differ between women and men, or between younger and older people.</b></li>
</ul>
<p>The review didn&rsquo;t test &ldquo;zone 2&rdquo; by name, and it doesn&rsquo;t say what share of participants were women.</p>
<h3>A review that took on the zone 2 hype</h3>
<p>A 2025 narrative review in <i>Sports Medicine</i>, titled &ldquo;Much Ado About Zone 2,&rdquo; looked at the case for zone 2 in the general public. Its authors found that the popular advice comes largely from observations of elite endurance athletes, who train for many hours a week and already have very high mitochondrial capacity. They concluded that current evidence doesn&rsquo;t support zone 2 as the best intensity for building mitochondria or fat-burning capacity, and that working above zone 2 matters for heart and metabolic health, especially for people with limited time to train.</p>
<p>A narrative review is one group&rsquo;s reading of the evidence, not a pooled analysis, so it&rsquo;s best read alongside the larger review above. Both point the same way: <b>steady cardio works, but it isn&rsquo;t uniquely powerful.</b></p>

<h2>What&rsquo;s overclaimed about zone 2</h2>
<ul>
<li><b>&ldquo;It&rsquo;s the best intensity for mitochondria.&rdquo;</b> Not shown. Intervals raised mitochondrial markers as much or more in less time.</li>
<li><b>&ldquo;Your watch knows your zone 2.&rdquo;</b> Fixed heart-rate percentages may not match your own threshold, and in the cyclist study the methods disagreed from person to person.</li>
<li><b>&ldquo;Zone 2 is a longevity treatment.&rdquo;</b> Fitness is linked to lower death rates in observational studies (see <a href="/fitness/vo2-max-women/">VO2 max for women</a>), but no trial shows that zone 2 in particular lengthens life.</li>
</ul>
<p>What zone 2 does have going for it: it&rsquo;s easy to recover from, easy to talk through, and a practical way to build up the minutes the guidelines call for.</p>

<h2>What this means for you</h2>
<ul class="ticks">
<li><b>Use the guidelines as your target.</b> 150 to 300 minutes a week of moderate activity, or 75 to 150 vigorous, or a mix.</li>
<li><b>Use the talk test.</b> If you can talk but not sing, you&rsquo;re in moderate territory, close to what most people call zone 2.</li>
<li><b>Easy and hard both count.</b> Steady cardio builds fitness; harder intervals are another well-studied option if you have less time. Our <a href="/fitness/vo2-max-women/">VO2 max guide</a> covers interval trials in midlife women.</li>
<li><b>Keep lifting.</b> Cardio doesn&rsquo;t replace <a href="/bones/strength-training-bone-density-menopause/">strength training for bone and muscle</a> around menopause.</li>
<li><b>Fit it in.</b> Brisk walks, cycling on flat ground and water aerobics all count, and short sessions add up.</li>
</ul>
<p>If you haven&rsquo;t been active, the guidelines advise starting low and going slow. If you have a heart condition, another health condition, an injury or symptoms, or haven&rsquo;t been active, check with your clinician before starting. Find more routines in <a href="/fitness/">Fitness</a> and the basics, including <a href="/foundations/deep-sleep-after-35/">deep sleep after 35</a>, in <a href="/foundations/">Sleep &amp; Foundations</a>.</p>""",
 [("Effects of Exercise Training on Mitochondrial and Capillary Growth in Human Skeletal Muscle: A Systematic Review and Meta-Regression (DOI 10.1007/s40279-024-02120-2)", "https://link.springer.com/article/10.1007/s40279-024-02120-2"),
  ("Much Ado About Zone 2: A Narrative Review Assessing the Efficacy of Zone 2 Training for Improving Mitochondrial Capacity and Cardiorespiratory Fitness in the General Population. Sports Medicine, 2025;55(7):1611&ndash;1624", "https://pubmed.ncbi.nlm.nih.gov/40560504/"),
  ("Meixner B, Filipas L, Holmberg HC, Sperlich B. Zone 2 Intensity: A Critical Comparison of Individual Variability in Different Submaximal Exercise Intensity Boundaries. Translational Sports Medicine, 2025;2025:2008291", "https://europepmc.org/api/getPdf?pmcid=PMC11986187"),
  ("U.S. Department of Health and Human Services. Physical Activity Guidelines for Americans, 2nd edition, 2018", "https://odphp.health.gov/sites/default/files/2019-09/Physical_Activity_Guidelines_2nd_edition.pdf"),
  ("Centers for Disease Control and Prevention. How to Measure Physical Activity Intensity", "https://www.cdc.gov/physical-activity-basics/measuring/index.html")]),

article("/hair/low-level-laser-therapy-hair/", "/hair/", "Hair",
 "Laser Caps and Combs (LLLT) for Hair Loss: Do They Work?",
 "Laser caps and combs (LLLT) for hair loss: do they work?",
 "Do laser caps and combs regrow hair in women? What sham-controlled trials found, what FDA clearance really means, and the eye-safety basics.",
 "2026-11-25",
 "Laser combs, caps and helmets promise thicker hair from a few minutes of red light a week. They&rsquo;re sold for home use and often advertised as &ldquo;FDA-cleared.&rdquo; Here&rsquo;s what the trials in women found, and what that label does and doesn&rsquo;t mean.",
 "In sham-controlled trials, women with pattern thinning who used a red-light laser comb for 26 weeks gained more hairs per square centimeter than women using a look-alike sham device, and a 2021 meta-analysis of seven randomized trials also favored the lasers. <b>The evidence is real but modest, mostly short-term and largely tied to device makers, and FDA clearance is not proof that a device works.</b>",
 "human-trial",
 [("Best evidence", "Two randomized, double-blind, sham-controlled trials in women (published together in 2014, 141 women randomized), plus a 2021 meta-analysis of 7 randomized trials in men and women"),
  ("Women included?", "Yes. The 2014 paper ran two trials only in women aged roughly 25 to 61 with female pattern hair loss; 94.7% of all participants were white"),
  ("Dose or protocol tested", "A red-light laser comb (655 nm) used 8 to 11 minutes per session, three times a week, for 26 weeks"),
  ("Bottom line", "A reasonable, low-risk option to ask a dermatologist about for pattern thinning. Expect small gains over months, not a transformation, and know that most devices were cleared without their own clinical trials")],
 """<h2>What is low-level laser therapy for hair?</h2>
<p>Low-level laser therapy (LLLT), also called photobiomodulation, shines low-power red light on the scalp. Home devices come as handheld combs, headbands, caps and helmets. Some use laser diodes, some use LEDs, and some mix both.</p>
<p>These devices are meant for <b>androgenetic alopecia</b>, the gradual pattern thinning known in women as female pattern hair loss. They aren&rsquo;t cleared for other kinds of hair loss. If you&rsquo;re not sure which you have, start with <a href="/hair/female-hair-loss-causes/">the main causes of hair loss in women</a>.</p>

<h2>What does &ldquo;FDA-cleared&rdquo; mean for a laser cap?</h2>
<p>Home hair lasers reach the market through the FDA&rsquo;s 510(k) pathway. Under 510(k), a company shows that its device is <i>substantially equivalent</i> to a device already legally sold: the same intended use, and either the same technology or different technology that doesn&rsquo;t raise new safety and effectiveness questions. The FDA then &ldquo;clears&rdquo; it.</p>
<p>That&rsquo;s different from <b>premarket approval</b> (PMA), the FDA&rsquo;s strictest route, used for high-risk Class III devices. PMA requires enough valid scientific evidence that the device is safe and effective. For a 510(k), the FDA says performance data <i>can</i> include clinical data, but bench testing is also accepted.</p>
<p>The public 510(k) summaries for hair lasers show how this works in practice:</p>
<table>
<tr><th>FDA file</th><th>Device type</th><th>Cleared for</th><th>Clinical study in the summary?</th></tr>
<tr><td>K112524 (2011)</td><td>Laser comb, 7 or 12 beams</td><td>Women with pattern hair loss (Ludwig-Savin I-4, II-1, II-2 or frontal), skin types I to IV</td><td>No. Nonclinical and performance testing, compared with an earlier comb</td></tr>
<tr><td>K132646 (2013)</td><td>Stationary laser hood, 650 nm</td><td>Men and women with pattern hair loss, skin types I to IV</td><td>No. Performance and electrical safety testing</td></tr>
<tr><td>K230134 (2023)</td><td>Laser comb, 650 nm</td><td>Men and women with pattern hair loss, skin types I to IV</td><td>No. Safety, electrical and laser-class testing, compared with earlier combs</td></tr>
</table>
<p>All three are Class II devices under the FDA&rsquo;s infrared lamp regulation. <b>A newer cap can be cleared because it resembles an older comb, without ever being tested on a single scalp.</b> &ldquo;FDA-cleared&rdquo; tells you the device met the bar for its class, not that the brand in your cart was shown to grow hair.</p>
<p>Note the skin-type limit, too. The clearances cover Fitzpatrick skin types I to IV, which leaves out darker skin types above IV.</p>

<h2>Do laser combs work for women? The sham-controlled trials</h2>
<p>The key trials in women were published in 2014 in the <i>American Journal of Clinical Dermatology</i> (Jimenez et al.). The paper reported four randomized, double-blind trials: two in women and two in men.</p>
<ul>
<li><b>Who:</b> 141 women with female pattern hair loss were randomized across the two women&rsquo;s trials. Ages across the study ran from 25 to 61, and 94.7% of participants were white.</li>
<li><b>Design:</b> Women used either a laser comb or a sham device that looked the same but gave off ordinary white light. Neither they nor the researchers knew which.</li>
<li><b>Protocol:</b> A 9-beam comb (655 nm, 11 minutes) or a 12-beam comb (635 and 655 nm, 8 minutes), three times a week for 26 weeks.</li>
<li><b>Measured:</b> The change in terminal (full-thickness) hairs per square centimeter in a small marked patch of scalp, counted from photos by an evaluator who didn&rsquo;t know the group.</li>
</ul>
<table>
<tr><th>Women&rsquo;s trial</th><th>Laser comb: hairs gained per cm&sup2;</th><th>Sham: hairs gained per cm&sup2;</th></tr>
<tr><td>9-beam comb</td><td>20.2</td><td>2.8</td></tr>
<tr><td>12-beam comb</td><td>20.6</td><td>3.0</td></tr>
</table>
<p>Both differences were statistically significant (p &lt; 0.0001). No serious side effects were reported with the comb in any of the four trials.</p>
<p><b>Limits worth knowing:</b> the trials lasted six months, so they don&rsquo;t show whether gains hold or what happens if you stop. They tested one company&rsquo;s combs (made by Lexington International, maker of the HairMax), and the paper describes the trials as run under that company&rsquo;s clinical-study procedures. A gain of about 20 hairs per square centimeter is measurable in a photo; whether you&rsquo;d notice it in the mirror is a separate question.</p>

<h2>What the meta-analysis of laser hair devices found</h2>
<p>A 2021 systematic review and meta-analysis in the <i>Journal of Clinical and Aesthetic Dermatology</i> (Lueangarun et al.) pooled seven double-blind, randomized, sham-controlled trials of home-use devices.</p>
<ul>
<li>Overall, the devices beat sham for hair growth, with a standardized mean difference of 1.27 (95% confidence interval 0.993 to 1.639). That&rsquo;s a statistical measure of effect size, not a hair count.</li>
<li>Benefits showed up in both men and women, and with both combs and helmets.</li>
<li>Devices using laser diodes alone did better (1.52) than those mixing lasers with LEDs (0.85).</li>
<li>The authors called LLLT &ldquo;potentially effective&rdquo; and asked for longer follow-up and head-to-head comparisons of devices.</li>
</ul>
<p>The review counted 32 home-use devices in the FDA&rsquo;s 510(k) database as of January 2020, far more than have been tested in trials. (Its title calls them &ldquo;FDA-approved,&rdquo; but the database it searched is for clearances.)</p>

<h2>Are laser caps safe for your eyes and scalp?</h2>
<p>The comb cleared in 2023 lists its lasers as Class 3R. The FDA groups that class with laser pointers and says it can be momentarily hazardous when viewed directly. The agency&rsquo;s general rule: <b>never look directly into any laser beam.</b> Follow the device&rsquo;s own instructions.</p>
<p>In the 2014 trials, no serious side effects were reported. If your scalp is irritated, broken or sun-damaged, ask a clinician before using any device on it.</p>

<h2>The honest bottom line</h2>
<ul class="ticks">
<li><b>Get the cause right first.</b> Lasers are cleared for pattern thinning. Low iron, thyroid problems and shedding after illness need different steps; see <a href="/hair/iron-ferritin-hair-loss/">iron, ferritin and hair loss</a> and <a href="/hair/thyroid-hair-loss/">thyroid and hair loss</a>.</li>
<li><b>The trials in women were positive but modest,</b> short, and tied to device makers.</li>
<li><b>Cleared isn&rsquo;t proven.</b> Most cleared devices were never tested in their own trial.</li>
<li><b>It&rsquo;s a months-long commitment.</b> The women&rsquo;s trials ran 26 weeks of sessions three times a week.</li>
<li><b>Compare options.</b> Ask about medicines too; see <a href="/hair/minoxidil-for-women/">minoxidil for women</a>. For red light on skin, see <a href="/skin/red-light-therapy-skin-over-40/">red light therapy for skin over 40</a>, and for an in-office option, <a href="/hair/prp-hair-loss-women/">PRP for hair loss in women</a>.</li>
</ul>
<h3>Questions to ask a board-certified dermatologist</h3>
<ul>
<li>Is my thinning female pattern hair loss, or something else?</li>
<li>Would a light device make sense for me alongside or instead of minoxidil?</li>
<li>Has the device I&rsquo;m considering been tested in a trial, or only cleared by equivalence?</li>
<li>How and when should we judge whether it&rsquo;s working?</li>
<li>Does my skin type fall within what the device was cleared for?</li>
</ul>
<p>More on thinning, shedding and treatments in <a href="/hair/">Hair</a>.</p>""",
 [("Jimenez JJ, Wikramanayake TC, Bergfeld W, et al. Efficacy and Safety of a Low-level Laser Device in the Treatment of Male and Female Pattern Hair Loss: A Multicenter, Randomized, Sham Device-controlled, Double-blind Study. American Journal of Clinical Dermatology, 2014;15(2):115&ndash;127", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3986893/"),
  ("Lueangarun S, Visutjindaporn P, Parcharoen Y, Jamparuang P, Tempark T. A Systematic Review and Meta-analysis of Randomized Controlled Trials of United States Food and Drug Administration-Approved, Home-use, Low-Level Light/Laser Therapy Devices for Pattern Hair Loss. Journal of Clinical and Aesthetic Dermatology, 2021;14(11):E64&ndash;E75", "https://pmc.ncbi.nlm.nih.gov/articles/PMC8675345/"),
  ("U.S. Food and Drug Administration. Premarket Notification 510(k)", "https://www.fda.gov/medical-devices/premarket-submissions-selecting-and-preparing-correct-submission/premarket-notification-510k"),
  ("U.S. Food and Drug Administration. Premarket Approval (PMA)", "https://www.fda.gov/medical-devices/premarket-submissions-selecting-and-preparing-correct-submission/premarket-approval-pma"),
  ("U.S. Food and Drug Administration. 510(k) summary K112524 (laser comb, 2011)", "https://www.accessdata.fda.gov/cdrh_docs/pdf11/K112524.pdf"),
  ("U.S. Food and Drug Administration. 510(k) summary K132646 (laser hood, 2013)", "https://www.accessdata.fda.gov/cdrh_docs/pdf13/k132646.pdf"),
  ("U.S. Food and Drug Administration. 510(k) summary K230134 (laser comb, 2023)", "https://www.accessdata.fda.gov/cdrh_docs/pdf23/K230134.pdf"),
  ("U.S. Food and Drug Administration. Frequently Asked Questions About Lasers", "https://www.fda.gov/radiation-emitting-products/laser-products-and-instruments/frequently-asked-questions-about-lasers")]),


]

# Articles Vita pulled in the review sheet: never built or listed (paths in _src/pulled.json).
_PULLED = set(_json.load(open(_os.path.join(_os.path.dirname(__file__), "pulled.json"), encoding="utf-8")))
ARTICLES = [a for a in ARTICLES if a["path"] not in _PULLED]
