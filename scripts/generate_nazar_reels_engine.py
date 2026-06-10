#!/usr/bin/env python3
"""Generate 100 vertical Nazar reels and caption metadata."""

from __future__ import annotations

import csv
import argparse
import json
import subprocess
import tempfile
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REELS_DIR = ROOT / "content/reels"
CSV_PATH = ROOT / "content/reel-captions.csv"
JSON_PATH = ROOT / "content/reels-engine.json"
FFMPEG = "/usr/bin/ffmpeg"
FONT_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf"
FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

WIDTH = 1080
HEIGHT = 1920
FPS = 24

CATEGORY_TAGS = {
    "coffee shops": ["#nazarapp", "#coffeeshop", "#quietmoments", "#ordinarybeauty"],
    "city walks": ["#nazarapp", "#citywalk", "#streetpoetry", "#noticing"],
    "train rides": ["#nazarapp", "#trainride", "#commuterlife", "#quietbeauty"],
    "family moments": ["#nazarapp", "#familymoments", "#tenderness", "#smallbeautifulthings"],
    "nostalgia": ["#nazarapp", "#nostalgia", "#memorykeeping", "#dailyritual"],
    "rain": ["#nazarapp", "#rainyday", "#softliving", "#mindfulmoments"],
    "nature": ["#nazarapp", "#naturemoments", "#slowdaily", "#presencepractice"],
    "travel": ["#nazarapp", "#travelmoments", "#noticingpractice", "#ordinarybeauty"],
    "quiet beauty": ["#nazarapp", "#quietbeauty", "#softlife", "#ordinarymagic"],
    "things people usually miss": ["#nazarapp", "#thingstomiss", "#noticing", "#everydaybeauty"],
}

QUESTIONS_BY_CATEGORY = {
    "coffee shops": [
        "What did you notice before your first sip today?",
        "What tiny cafe detail stayed with you longer than expected?",
        "What did someone leave behind that told a quiet story?",
    ],
    "city walks": [
        "What small street moment did you almost walk past?",
        "What did the city show you when you slowed down?",
        "What ordinary scene felt briefly cinematic today?",
    ],
    "train rides": [
        "What did you notice between where you were and where you were going?",
        "What small thing changed when the train started moving?",
        "What did the window give back to you today?",
    ],
    "family moments": [
        "What small family gesture did you want to keep?",
        "What ordinary kindness happened in your home today?",
        "What detail made someone feel especially familiar?",
    ],
    "nostalgia": [
        "What object brought a whole year back for a second?",
        "What memory returned through texture, sound, or smell?",
        "What did you find that still seemed to remember you?",
    ],
    "rain": [
        "What did the rain make you notice differently?",
        "What changed color when the weather changed?",
        "What small sound did the rain make louder?",
    ],
    "nature": [
        "What did the living world do quietly near you today?",
        "What small natural thing asked for your attention?",
        "What did you see outside that felt unhurried?",
    ],
    "travel": [
        "What detail from the journey felt worth keeping?",
        "What did an unfamiliar place make newly beautiful?",
        "What small travel moment felt like it belonged only to you?",
    ],
    "quiet beauty": [
        "What softened the room today?",
        "What ordinary thing looked briefly forgiven?",
        "What small beauty did you catch before it changed?",
    ],
    "things people usually miss": [
        "What did you notice that most people would miss?",
        "What tiny detail proved the day was alive?",
        "What small thing kept happening quietly in the background?",
    ],
}

CTAS = [
    "Try Nazar.",
    "Keep one small thing in Nazar.",
    "Notice with Nazar.",
    "Save it in Nazar.",
    "Open Nazar when something small stays with you.",
]

PALETTES = [
    {"bg": "#F7F1E7", "accent": "#B98243", "muted": "#9C9183", "ink": "#252018"},
    {"bg": "#EEF0F5", "accent": "#534AB7", "muted": "#8A90A3", "ink": "#22283A"},
    {"bg": "#F3E6DC", "accent": "#D85A30", "muted": "#A47D6A", "ink": "#33251D"},
    {"bg": "#F5EBD9", "accent": "#BA7517", "muted": "#A88C65", "ink": "#33281C"},
    {"bg": "#E9F0EA", "accent": "#1D9E75", "muted": "#789184", "ink": "#1F3028"},
    {"bg": "#E9EDF4", "accent": "#6E7FA8", "muted": "#8B90A0", "ink": "#252A3A"},
    {"bg": "#F1EAE1", "accent": "#8F6A4A", "muted": "#9E9185", "ink": "#2F2923"},
    {"bg": "#F6EEDC", "accent": "#C28A2C", "muted": "#A18B63", "ink": "#302719"},
    {"bg": "#ECE8DC", "accent": "#085041", "muted": "#7F877B", "ink": "#25342B"},
    {"bg": "#F4E8EE", "accent": "#D4537E", "muted": "#A98291", "ink": "#33232B"},
]

OBSERVATIONS_BY_CATEGORY = {
    "coffee shops": [
        ("before the first sip", "The barista wiped the same clean spot three times while waiting for the milk to steam."),
        ("someone left in a hurry", "A half moon of lipstick stayed on the rim of the paper cup after she ran for the bus."),
        ("table by the window", "The little sugar packets had been arranged into a wall by someone trying not to check their phone."),
        ("coffee cooling", "The espresso crema broke slowly, like a small brown cloud deciding to disappear."),
        ("two strangers, one outlet", "Two laptops shared one outlet under the table, their cords touching like quiet acquaintances."),
        ("receipt folded twice", "A receipt was folded into a tiny square and left under the saucer like a secret."),
        ("rain at the glass", "Everyone looked up at the same time when rain began ticking against the front window."),
        ("the regular's chair", "The man in the green coat sat down before ordering, and the barista had already started his drink."),
        ("near closing", "The chairs on the tables made the whole cafe look like it was holding its breath."),
        ("foam heart", "The heart in my coffee lasted only until the second sip, which made it feel more generous."),
    ],
    "city walks": [
        ("crosswalk tenderness", "An older man fixed the collar of the woman beside him before the light changed."),
        ("morning delivery", "A stack of newspapers landed on the sidewalk with a soft, tired slap."),
        ("window plants", "Three apartment plants leaned toward the same narrow strip of sun like they had agreed on it."),
        ("pigeon decision", "A pigeon stopped in the middle of the pavement as if reconsidering its whole morning."),
        ("corner fruit stand", "The oranges at the corner store were stacked so carefully they looked like borrowed sunlight."),
        ("blue door", "Someone had painted only the inside edge of the door blue, a private color for coming home."),
        ("bus stop", "A woman at the bus stop held flowers upside down to keep them from opening too soon."),
        ("after school", "A child's backpack bounced behind him while he told a story with both hands."),
        ("laundromat window", "The dryers turned all the white shirts into slow weather."),
        ("streetlight at noon", "One streetlight stayed on at noon, pale and unnecessary, but trying anyway."),
    ],
    "train rides": [
        ("between stations", "The tunnel made everyone's reflection appear in the window at once."),
        ("sleeping commuter", "The man across from me woke up exactly one stop before his stop, like his body remembered for him."),
        ("ticket corner", "A ticket stub softened at the corner where someone kept rubbing it with their thumb."),
        ("platform goodbye", "She waved until the train moved, then kept waving at the empty track."),
        ("overhead announcement", "The announcement crackled so gently that even the delay sounded apologetic."),
        ("window blur", "The fields outside blurred into one green sentence I could not read fast enough."),
        ("shared table", "Four strangers placed their coffees in the same careful square on the train table."),
        ("late train", "A boy counted the blue seats with his finger while everyone else sighed at the delay."),
        ("quiet carriage", "The quiet carriage was not silent; it was full of pages turning and coats shifting."),
        ("arrival light", "When we came out of the tunnel, the whole carriage filled with gold for three seconds."),
    ],
    "family moments": [
        ("kitchen doorway", "My father stood in the kitchen doorway eating toast over a plate he did not need."),
        ("voice note", "My mother laughed at the end of a voice note because she forgot what she was saying."),
        ("small shoes", "The smallest shoes by the door were placed perfectly side by side by no adult at all."),
        ("after dinner", "Someone left one green bean on the plate, and my sister called it a survivor."),
        ("birthday candle", "The candle smoke curled toward my grandmother before anyone started clapping."),
        ("folded blanket", "The blanket on the sofa still had the shape of the person who had just left."),
        ("phone brightness", "My brother dimmed my mother's phone for her without pausing the conversation."),
        ("old recipe", "The recipe card had oil spots exactly where her hand must have rested each time."),
        ("bath time", "A rubber duck floated alone after the bathwater drained, looking professionally patient."),
        ("front step", "My aunt brushed invisible lint from my coat before saying goodbye."),
    ],
    "nostalgia": [
        ("jacket pocket", "I found a movie ticket in my jacket pocket, soft at the fold from a night I thought I forgot."),
        ("old password", "An old password hint brought back an entire apartment I have not lived in for years."),
        ("school smell", "The hallway smelled like floor polish and suddenly I was ten, carrying a too-heavy bag."),
        ("photo corner", "In the photo, my grandfather's hand is blurred because he was always mid-gesture."),
        ("cassette case", "The empty cassette case clicked shut with the exact sound of my brother's room."),
        ("childhood mug", "The chipped mug at my mother's house still makes tea taste like being home sick from school."),
        ("old keys", "A key I no longer need stayed on the ring because I liked the weight of that year."),
        ("recipe drawer", "The drawer smelled faintly of vanilla, paper, and every December we tried to recreate."),
        ("summer towel", "A beach towel from childhood still had sand caught in one seam."),
        ("forgotten bookmark", "The bookmark was a bus ticket from a city where I used to know the shortcuts."),
    ],
    "rain": [
        ("first drops", "The first drops made dark coins on the pavement before the whole street changed color."),
        ("umbrella sound", "Under the umbrella, the rain sounded closer than my own thoughts."),
        ("window trail", "One raindrop found another and they became a faster thing together."),
        ("wet sleeves", "My sleeves were damp at the wrists, which made holding the warm cup feel more dramatic."),
        ("after rain", "After the rain stopped, every parked car kept a small trembling sky on its roof."),
        ("storm light", "The room went green for a second before the thunder arrived."),
        ("bus window", "A child traced the raindrops down the bus window like they were choosing a path."),
        ("rain smell", "The stairwell smelled like wet wool and someone's dinner coming home late."),
        ("puddle city", "The puddle held the building upside down better than the building held itself."),
        ("drain song", "The drain outside sang a low, steady note after everyone else went inside."),
    ],
    "nature": [
        ("bee pause", "A bee stayed inside one flower so long it looked like it had found a room."),
        ("leaf shadow", "The leaf shadows kept changing shape on my arm while I tried to stay still."),
        ("snail crossing", "The snail crossed the path with the confidence of something that does not negotiate with time."),
        ("morning bird", "One bird began before the others, then waited as if embarrassed by its own hope."),
        ("moss wall", "Moss had made a soft green country out of the north side of the wall."),
        ("dogwood petals", "The petals on the pavement looked less fallen than placed."),
        ("wind in grass", "The wind moved through the grass in sections, like a hand smoothing a blanket."),
        ("garden hose", "Water gathered at the hose mouth before falling, one clear bead at a time."),
        ("spider web", "The web held three drops of rain in a perfect uneven triangle."),
        ("evening tree", "At dusk, the tree outside my window became one dark thought full of birds."),
    ],
    "travel": [
        ("hotel hallway", "The hotel hallway carpet made everyone's suitcase sound softer than it was."),
        ("airport gate", "At the gate, a child slept across two chairs while departures changed above him."),
        ("foreign grocery", "The grocery store in another country made onions feel newly interesting."),
        ("map fold", "The paper map tore slightly on the fold where we kept deciding to turn left."),
        ("balcony morning", "The balcony chair was still wet from night air when I sat down with coffee."),
        ("rental key", "The rental key was heavier than expected, like the place wanted to be taken seriously."),
        ("train window", "A town I will never know passed by with laundry moving on one balcony."),
        ("museum bench", "The museum bench held three people resting from beauty in complete silence."),
        ("postcard rack", "The postcard rack spun too fast and showed the whole city in a blur."),
        ("last morning", "On the last morning, even the elevator button felt like part of the trip."),
    ],
    "quiet beauty": [
        ("golden dishes", "At 6:12 the whole apartment turned gold, including the pile of dishes."),
        ("made bed", "The pillow kept the dent of my head for a few minutes after I got up."),
        ("lamp click", "The lamp clicked on and made the room look like it had forgiven me."),
        ("warm laundry", "The laundry was still warm when I folded it, and the whole room felt briefly kind."),
        ("open book", "The book stayed open on the table like it trusted me to come back."),
        ("glass water", "The glass of water caught a rectangle of window light and held it without spilling."),
        ("quiet sink", "One spoon in the sink reflected the ceiling light like a tiny moon."),
        ("curtain edge", "The curtain lifted once in the breeze and showed the room how to breathe."),
        ("soft sweater", "The sweater on the chair looked like someone sitting there in a gentler version of the day."),
        ("blue dusk", "Blue dusk entered the room slowly enough that I did not notice until everything was softer."),
    ],
    "things people usually miss": [
        ("elevator sigh", "The elevator made its tired little sigh before the doors opened."),
        ("receipt shadow", "The receipt under the glass made a shadow thinner than a thread."),
        ("door paint", "The paint was worn away exactly where every hand expects the door to open."),
        ("stair dust", "Dust gathered in the stair corner like a soft record of everyone leaving."),
        ("button thread", "One loose thread on my coat button moved every time I breathed."),
        ("soap sliver", "The last sliver of soap had gone translucent at the edge."),
        ("chair sound", "The empty chair made a small wooden sound when the floor settled."),
        ("phone heat", "The phone was warm after a long call, like the conversation had stayed inside it."),
        ("key bowl", "The keys in the bowl made one bright note when someone came home."),
        ("mirror corner", "The corner of the mirror held a reflection of the sky no one was looking for."),
    ],
}


def build_items() -> list[dict]:
    items: list[dict] = []
    day = 1
    durations = [7, 8, 9, 10, 11, 12, 8, 9, 10, 11]
    for category, observations in OBSERVATIONS_BY_CATEGORY.items():
        for category_index, (hook, observation) in enumerate(observations):
            palette = PALETTES[(day - 1) % len(PALETTES)]
            question = QUESTIONS_BY_CATEGORY[category][category_index % len(QUESTIONS_BY_CATEGORY[category])]
            hashtags = " ".join(CATEGORY_TAGS[category])
            cta = CTAS[(day - 1) % len(CTAS)]
            formatted_caption = f"{observation}\n\n{question}\n\n{hashtags}\n\n{cta}"
            items.append(
                {
                    "reel": day,
                    "filename": f"nazar-reel-{day:03d}.mp4",
                    "category": category,
                    "duration": durations[(day - 1) % len(durations)],
                    "hook": hook,
                    "observation": observation,
                    "caption": observation,
                    "question": question,
                    "hashtags": hashtags,
                    "cta": cta,
                    "formatted_caption": formatted_caption,
                    "palette": palette,
                }
            )
            day += 1
    return items


def textfile(temp_dir: Path, name: str, value: str) -> Path:
    path = temp_dir / f"{name}.txt"
    path.write_text(value)
    return path


def wrap_for_video(value: str, width: int) -> str:
    return "\n".join(textwrap.wrap(value, width=width, break_long_words=False))


def drawtext(
    text_path: Path,
    font: str,
    size: int,
    color: str,
    x: str,
    y: str,
    line_spacing: int = 12,
    alpha: str = "1",
) -> str:
    return (
        "drawtext="
        f"fontfile='{font}':"
        f"textfile='{text_path}':"
        f"fontsize={size}:"
        f"fontcolor={color}:"
        f"x={x}:"
        f"y={y}:"
        f"line_spacing={line_spacing}:"
        f"alpha='{alpha}'"
    )


def render_reel(item: dict, temp_dir: Path) -> None:
    output = REELS_DIR / item["filename"]
    output.unlink(missing_ok=True)
    palette = item["palette"]
    duration = item["duration"]
    hook_file = textfile(temp_dir, f"hook-{item['reel']:03d}", item["hook"].upper())
    obs_file = textfile(temp_dir, f"obs-{item['reel']:03d}", wrap_for_video(item["observation"], 28))
    brand_file = textfile(temp_dir, f"brand-{item['reel']:03d}", "nazar")
    tag_file = textfile(temp_dir, f"tag-{item['reel']:03d}", item["category"])
    micro_file = textfile(temp_dir, f"micro-{item['reel']:03d}", "a daily ritual of noticing")
    fade_alpha = f"if(lt(t,0.8),t/0.8,if(gt(t,{duration - 0.8}),({duration}-t)/0.8,1))"

    filters = [
        f"[1:v]format=rgba,colorchannelmixer=aa=0.16,boxblur=90:1[orb1]",
        f"[2:v]format=rgba,colorchannelmixer=aa=0.11,boxblur=110:1[orb2]",
        f"[0:v][orb1]overlay=x='-460+38*t':y='100+22*sin(t*0.55)'[b1]",
        f"[b1][orb2]overlay=x='540-28*t':y='1120+24*cos(t*0.45)'[b2]",
        (
            "[b2]"
            "drawbox=x=86:y=282:w=908:h=1188:color=white@0.28:t=fill,"
            f"drawbox=x=86:y=282:w=908:h=1188:color={palette['accent']}@0.18:t=3,"
            f"drawbox=x=136:y=1268:w=808:h=2:color={palette['accent']}@0.36:t=fill,"
            f"{drawtext(hook_file, FONT_SANS_BOLD, 44, palette['muted'], '136', '376', 14, fade_alpha)},"
            f"{drawtext(obs_file, FONT_SERIF, 70, palette['ink'], '136', '520', 18, fade_alpha)},"
            f"{drawtext(brand_file, FONT_SERIF, 42, palette['ink'], '136', '1354', 10, fade_alpha)},"
            f"{drawtext(tag_file, FONT_SANS, 24, palette['muted'], '136', '1410', 10, fade_alpha)},"
            f"{drawtext(micro_file, FONT_SANS, 25, palette['muted'], 'w-text_w-136', '1358', 10, fade_alpha)},"
            f"drawtext=fontfile='{FONT_SANS}':text='save if you noticed it too':fontsize=31:fontcolor={palette['muted']}:x=(w-text_w)/2:y=1618:alpha='{fade_alpha}',"
            f"fade=t=in:st=0:d=0.8,fade=t=out:st={duration - 0.8}:d=0.8,"
            "format=yuv420p[v]"
        ),
    ]

    subprocess.run(
        [
            FFMPEG,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "lavfi",
            "-i",
            f"color=c={palette['bg']}:s={WIDTH}x{HEIGHT}:r={FPS}:d={duration}",
            "-f",
            "lavfi",
            "-i",
            f"color=c={palette['accent']}:s=900x900:r={FPS}:d={duration}",
            "-f",
            "lavfi",
            "-i",
            f"color=c={palette['muted']}:s=760x760:r={FPS}:d={duration}",
            "-filter_complex",
            ";".join(filters),
            "-map",
            "[v]",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "34",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(output),
        ],
        check=True,
    )


def write_metadata(items: list[dict]) -> None:
    JSON_PATH.write_text(json.dumps({"version": "1.0.0", "items": items}, indent=2) + "\n")

    with CSV_PATH.open("w", newline="") as output:
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "reel",
                "filename",
                "category",
                "duration",
                "hook",
                "observation",
                "caption",
                "question",
                "hashtags",
                "cta",
                "formatted_caption",
            ],
        )
        writer.writeheader()
        for item in items:
            writer.writerow(
                {
                    "reel": item["reel"],
                    "filename": f"reels/{item['filename']}",
                    "category": item["category"],
                    "duration": item["duration"],
                    "hook": item["hook"],
                    "observation": item["observation"],
                    "caption": item["caption"],
                    "question": item["question"],
                    "hashtags": item["hashtags"],
                    "cta": item["cta"],
                    "formatted_caption": item["formatted_caption"],
                }
            )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=int, default=1, help="First 1-based reel number to render.")
    parser.add_argument("--count", type=int, default=100, help="Number of reels to render.")
    parser.add_argument("--clean", action="store_true", help="Remove existing MP4 files before rendering.")
    parser.add_argument("--metadata-only", action="store_true", help="Write JSON/CSV metadata without rendering videos.")
    args = parser.parse_args()

    REELS_DIR.mkdir(parents=True, exist_ok=True)
    if args.clean:
        for path in REELS_DIR.glob("*.mp4"):
            path.unlink()

    items = build_items()
    write_metadata(items)
    if args.metadata_only:
        print(f"wrote {JSON_PATH}")
        print(f"wrote {CSV_PATH}")
        return

    start_index = max(args.start - 1, 0)
    end_index = min(start_index + args.count, len(items))
    render_items = items[start_index:end_index]

    with tempfile.TemporaryDirectory(prefix="nazar-reels-") as temp:
        temp_dir = Path(temp)
        for item in render_items:
            render_reel(item, temp_dir)
            print(f"rendered {item['filename']}")

    print(f"rendered {len(render_items)} reels in {REELS_DIR}")
    print(f"metadata covers {len(items)} reels")
    print(f"wrote {CSV_PATH}")


if __name__ == "__main__":
    main()
