"""Workflow videos for the project pages.

Pure data plus HTML helpers, no side effects, so build_site.py and one off
patch scripts can both import it. Video files live in /video/ at the site
root (H.264 MP4, faststart, no audio track) with a WebP poster beside each.
"""

VIDEOS = {
    "mhh": [
        dict(
            id="mhh-v01",
            src="/video/mhh_v01_linking_models.mp4",
            poster="/video/mhh_v01_poster.webp",
            dur="1:31",
            title="Linking the structural model and acquiring shared coordinates",
            shows=("Inside the architectural model I open Manage Links, bring in the structural "
                   "model from the project's cloud folder, check it in 3D against the site, then "
                   "acquire coordinates from the link so both disciplines share one survey point."),
            chapters=[(0, "Manage Links"), (5, "Link the structural model from the cloud"),
                      (30, "Check the link in 3D"), (45, "Acquire coordinates from the link"),
                      (65, "Review the federated model")],
            tags=["Revit links", "Shared coordinates", "Federation", "Cloud models"],
            see=("model-federation", "01 Model federation"),
        ),
        dict(
            id="mhh-v02",
            src="/video/mhh_v02_cloud_collaboration.mp4",
            poster="/video/mhh_v02_poster.webp",
            dur="1:23",
            title="Moving the structural model into the cloud for team worksharing",
            shows=("From the structural model I run Collaborate in Cloud, save it into the Structural "
                   "folder of the Hospital Project in Autodesk Docs, synchronize with central, then "
                   "confirm the cloud model sits in the right folder from Revit Home."),
            chapters=[(0, "The structural model"), (15, "Collaborate in Cloud, pick the folder"),
                      (25, "Save as cloud model"), (50, "Check it in Autodesk Docs"),
                      (65, "Synchronize with central"), (75, "Confirm in project files")],
            tags=["Autodesk Construction Cloud", "Cloud worksharing", "Synchronize with central", "CDE"],
            see=("common-data-environment", "07 Common data environment"),
        ),
    ],
}

SECTION_ID = "workflow-on-video"
TOC_LABEL = "Watch in Revit"
# sheet number -> video id, for the "watch this step" link on the matching sheet
SHEET_LINKS = {6: "mhh-v01", 12: "mhh-v02"}


def _ts(s):
    return f"{s // 60}:{s % 60:02d}"


def _card(i, v):
    chaps = "".join(
        f'<li><button type="button" class="vc-ch" data-t="{t}"><span class="mono">{_ts(t)}</span>{lab}</button></li>'
        for t, lab in v["chapters"])
    tags = "".join(f"<li>{t}</li>" for t in v["tags"])
    return f"""<article class="vc reveal" id="{v['id']}">
  <div class="vc-media">
   <video preload="none" playsinline muted controls controlslist="nodownload noremoteplayback" disablepictureinpicture
     width="1280" height="686" poster="{v['poster']}" aria-label="{v['title']}, screen recording, {v['dur']}, no audio">
    <source src="{v['src']}" type="video/mp4">
   </video>
   <button type="button" class="vc-play" aria-label="Play: {v['title']}"><span class="vc-btn" aria-hidden="true"></span><span class="vc-dur mono">{v['dur']}</span></button>
  </div>
  <div class="vc-body">
   <div class="vc-k mono"><span>Clip {i + 1:02d}</span><span>{v['dur']} · Revit 2027 · no audio</span></div>
   <h3>{v['title']}</h3>
   <p>{v['shows']}</p>
   <div class="vc-chl mono">Jump to</div>
   <ol class="vc-chs">{chaps}</ol>
   <ul class="vc-tags mono">{tags}</ul>
   <a class="vc-see mono" href="#{v['see'][0]}">Full write up: {v['see'][1]} <i>→</i></a>
  </div>
 </article>"""


def section_html(slug):
    vs = VIDEOS.get(slug)
    if not vs:
        return ""
    total = sum(int(m) * 60 + int(s) for m, s in (v["dur"].split(":") for v in vs))
    cards = "".join(_card(i, v) for i, v in enumerate(vs))
    return f"""<section class="sheet vids" id="{SECTION_ID}">
 <div class="wrap">
  <div class="sh-hdr mono"><span>Video · {len(vs):02d} clips</span><span>Screen recordings&nbsp;&nbsp;·&nbsp;&nbsp;Revit 2027&nbsp;&nbsp;·&nbsp;&nbsp;Autodesk Construction Cloud</span></div>
  <div class="vids-h">
   <div class="kicker">Watch the workflow</div>
   <h2>Federation and cloud worksharing, recorded in Revit</h2>
   <p>The case study below shows the results. These {len(vs)} clips show the setup work behind them, about {round(total / 60)} minutes in total, both silent. Use the chapter links to skip straight to a step.</p>
  </div>
  <div class="vids-g">{cards}</div>
 </div>
</section>"""


def toc_link():
    return f'<a href="#{SECTION_ID}"><span class="mono">▶</span>{TOC_LABEL}</a>'


def sheet_link(num, slug="mhh"):
    vid = SHEET_LINKS.get(num)
    v = next((v for v in VIDEOS.get(slug, []) if v["id"] == vid), None)
    if not v:
        return ""
    return f'<a class="watch mono" href="#{v["id"]}"><span aria-hidden="true">▶</span> Watch this step in Revit · {v["dur"]}</a>'


def card_badge(slug):
    vs = VIDEOS.get(slug)
    return f'<span class="pc-vid mono">▶ {len(vs)} workflow videos</span>' if vs else ""
