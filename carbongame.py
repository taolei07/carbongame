import base64
import html
import json
import mimetypes
import random
import time
from pathlib import Path
import streamlit as st
from supabase import create_client, Client
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# ============================================================
# Page Setup
# ============================================================
st.set_page_config(
    page_title="Carbon Match: Carbon Showdown v2",
    layout="wide",
)

TABLE = "carbon_match_games"
RULES_VERSION = 3

# ============================================================
# Supabase Connection
# ============================================================
@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["supabase_url"]
    key = st.secrets["supabase_key"]
    return create_client(url, key)


supabase = get_supabase()

# ============================================================
# Bilingual Text
# The new version keeps both dictionaries. The visible default is EN;
# change LANG = "ZH" below if you want the interface to be Chinese.
# ============================================================
LANG_TEXT = {
    "EN": {
        "page_title": "🃏 Carbon Match: Carbon Showdown",
        "room_caption": "Enter the same room code with your opponent, choose your role and profession, then battle online.",
        "room_input_label": "Room Code",
        "you_are": "You are",
        "profession_label": "Choose your profession",
        "join_create": "Join / Create Room",
        "room_warn": "Please enter a room code first.",
        "leave_room": "🚪 Leave Room",
        "room_header": "Room: {room} ｜ You are: {player} ｜ Profession: {profession}",
        "deck_status": "📦 Deck Status",
        "cards_remaining": "Cards Remaining: {count} / 60",
        "current_turn": "📍 Current Turn",
        "current_ap": "⚡ Current AP",
        "score_label": "⭐ Score",
        "restart": "🔄 Restart Game",
        "game_settled": "GAME SETTLED",
        "game_over_msg": "{winner} wins with {score} points!",
        "p1_zone": "🔵 Player 1 Zone",
        "p2_zone": "🔴 Player 2 Zone",
        "you_suffix": " (You)",
        "your_turn": "⚡ Your turn (Remaining AP: {ap})",
        "opp_turn": "⏳ Opponent's turn, please wait...",
        "current_score": "Current Score: {score}",
        "profession_display": "Profession: {profession}",
        "draw_card": "🎴 Draw Card (-1 AP)",
        "neutralize": "🌿 Neutralize (0 pts)",
        "end_turn": "⏭️ End Turn",
        "draw_warn": "Insufficient AP or the deck is empty.",
        "neutral_warn_no_pair": "No opposite-color cards available for pairing.",
        "neutral_warn_few": "The staging area has fewer than 2 cards.",
        "hand_title": "🎒 {player}'s Hand Cards",
        "hand_empty": "Hand is empty",
        "staging_title": "📥 {player}'s Staging Area",
        "staging_empty": "Staging area is empty",
        "scored_title": "🏆 {player} Scored Area (Total Score: {score})",
        "scored_empty": "No pairs in scored area yet",
        "pair_label": "Pair #{number}",
        "push_hint": "👉 Push Active: choose a card from this staging area.",
        "single_swap_hint_own": "👉 Single Swap Active: choose your own staging card.",
        "single_swap_hint_opp": "👉 Single Swap Active: choose an opponent staging card.",
        "steal_staging_hint": "👉 Steal Staging Active: choose an opponent staging card.",
        "steal_hint": "👉 Steal Active: choose an opponent Power Card.",
        "destroy_hint": "👉 Destroy Active: choose an opponent hand card.",
        "ap_warn": "⚠️ Insufficient AP.",
        "play_btn": "Play #{number}",
        "push_btn": "Push #{number}",
        "select_btn": "Select #{number}",
        "swap_btn": "Swap #{number}",
        "steal_btn": "Steal #{number}",
        "destroy_btn": "Destroy #{number}",
        "ban_btn": "🛑 Ban Power Card",
        "use_profession": "Use Profession Ability",
        "profession_used": "This profession ability has already been used.",
        "regulator_ready": "Use Emissions Regulator: make the opponent's next Power Card cost +1 AP.",
        "regulator_applied": "Emissions Regulator applied: the opponent's next Power Card costs +1 AP.",
        "regulator_debuff_active": "⚠️ Debuff active: your next Power Card costs +1 AP.",
        "peek_card": "Peeked Card",
        "peek_empty": "The deck is empty, so there is no next card to see.",
        "peek_note": "Only you can see this peeked card.",
        "ban_window": "{player} played {card}. You have {seconds} seconds to use Ban.",
        "ban_wait": "Waiting {player}'s 5-second Ban window...",
        "ban_cancelled": "{player}'s {card} was blocked by Ban.",
        "power_resolved": "{player}'s {card} resolved after the Ban window.",
        "ban_unavailable": "Ban can only be used during an opponent's 5-second reaction window.",
        "chaos_title": "Chaos Card",
        "chaos_good_free": "Chaos effect: your next Power Card costs 0 AP.",
        "chaos_good_score": "Chaos effect: you gained 2 points.",
        "chaos_bad_score": "Chaos effect: you lost 2 points.",
        "chaos_bad_double": "Chaos effect: your next Power Card costs double AP.",
        "chaos_neutral_peek": "Chaos effect: you may see the next card without drawing it.",
        "chaos_status_free": "✨ Chaos active: your next Power Card costs 0 AP.",
        "chaos_status_double": "⚠️ Chaos active: your next Power Card costs double AP.",
        "chaos_status_peek": "👁️ Chaos active: you may see the next card without drawing it.",

        "draw_number": "{player} drew number card [{value}-{color}] into the staging area.",
        "draw_power": "{player} drew Power Card [{card}].",
        "draw_chaos": "{player} drew a Chaos Card.",
        "game_start": "🎮 Game started! Carbon Match begins. Player 1 goes first.",
        "end_turn_log": "Turn passed: it is now {player}'s turn.",
        "neutral_log": "{player} neutralized mixed pair {value}: 0 points.",
        "black_pair": "{player} scored a black pair {value}: {points} points.",
        "red_pair": "{player} scored a red pair {value}: {points} points.",
        "plus_ap": "{player} used +1 AP and gained 1 AP.",
        "steal_staging_prepare": "{player} is choosing an opponent staging card to steal.",
        "steal_staging_done": "{player} stole {card} from the opponent's staging area.",
        "single_swap_prepare": "{player} is preparing Single Swap.",
        "single_swap_locked": "{player} selected {card} for Single Swap.",
        "single_swap_done": "{player} swapped {own} with {target}.",
        "push_prepare": "{player} is preparing Push.",
        "push_done": "{player} pushed {card} to the opponent.",
        "steal_prepare": "{player} is preparing Steal.",
        "steal_done": "{player} stole Power Card [{card}] from the opponent's hand.",
        "destroy_prepare": "{player} is preparing Destroy.",
        "destroy_done": "{player} destroyed the opponent's card [{card}].",
        "all_swap_removed": "Steal Staging",
        "reshuffle_done": "{player} reshuffled the remaining deck.",
        "peek_done": "{player} used Peek Next Card.",
        "game_over": "Final settlement: Player 1 {p1} points, Player 2 {p2} points. Winner: {winner}.",
        "room_profession_locked": "Profession locked for this room: {profession}.",
        "waiting_profession": "Waiting for the other player to choose a profession.",
        "auditor_start": "Carbon Auditor started with two Peek Next Cards.",
    },
    "ZH": {
        "page_title": "🃏 碳匹配：碳对决",
        "room_caption": "输入相同房间号，选择玩家位置和职业，然后开始在线对战。",
        "room_input_label": "房间号",
        "you_are": "你是",
        "profession_label": "选择职业",
        "join_create": "加入 / 创建房间",
        "room_warn": "请先输入房间号。",
        "leave_room": "🚪 离开房间",
        "room_header": "房间：{room} ｜ 你是：{player} ｜ 职业：{profession}",
        "deck_status": "📦 牌堆状态",
        "cards_remaining": "剩余卡牌：{count} / 60",
        "current_turn": "📍 当前回合",
        "current_ap": "⚡ 当前行动点",
        "score_label": "⭐ 分数",
        "restart": "🔄 重新开始",
        "game_settled": "游戏结算",
        "game_over_msg": "{winner} 以 {score} 分获胜！",
        "p1_zone": "🔵 玩家1区域",
        "p2_zone": "🔴 玩家2区域",
        "you_suffix": "（你）",
        "your_turn": "⚡ 你的回合（剩余行动点：{ap}）",
        "opp_turn": "⏳ 对手回合，请稍候……",
        "current_score": "当前分数：{score}",
        "profession_display": "职业：{profession}",
        "draw_card": "🎴 抽牌（-1行动点）",
        "neutralize": "🌿 中和（0分）",
        "end_turn": "⏭️ 结束回合",
        "draw_warn": "行动点不足或牌堆为空。",
        "neutral_warn_no_pair": "暂存区没有可配对的异色牌。",
        "neutral_warn_few": "暂存区卡牌少于2张。",
        "hand_title": "🎒 {player} 的手牌",
        "hand_empty": "手牌为空",
        "staging_title": "📥 {player} 的暂存区",
        "staging_empty": "暂存区为空",
        "scored_title": "🏆 {player} 得分区（总分：{score}）",
        "scored_empty": "得分区暂无配对",
        "pair_label": "配对 #{number}",
        "push_hint": "👉 推送激活：选择这个暂存区的一张牌。",
        "single_swap_hint_own": "👉 单卡交换激活：选择自己的暂存牌。",
        "single_swap_hint_opp": "👉 单卡交换激活：选择对手暂存区的牌。",
        "steal_staging_hint": "👉 暂存区偷取激活：选择对手暂存区的牌。",
        "steal_hint": "👉 偷取激活：选择对手的一张 Power Card。",
        "destroy_hint": "👉 销毁激活：选择对手手牌的一张牌。",
        "ap_warn": "⚠️ 行动点不足。",
        "play_btn": "出牌 #{number}",
        "push_btn": "推送 #{number}",
        "select_btn": "选择 #{number}",
        "swap_btn": "交换 #{number}",
        "steal_btn": "偷取 #{number}",
        "destroy_btn": "销毁 #{number}",
        "ban_btn": "🛑 禁止 Power Card",
        "use_profession": "使用职业能力",
        "profession_used": "这个职业能力本局已经使用过。",
        "regulator_ready": "使用排放监管员：让对手下一张 Power Card 额外消耗1行动点。",
        "regulator_applied": "排放监管员已生效：对手下一张 Power Card 额外消耗1行动点。",
        "regulator_debuff_active": "⚠️ Debuff 生效：你的下一张 Power Card 额外消耗1行动点。",
        "peek_card": "透视到的牌",
        "peek_empty": "牌堆为空，没有下一张牌可以查看。",
        "peek_note": "只有你能看到这张透视牌。",
        "ban_window": "{player} 使用了 {card}。你有 {seconds} 秒可以使用 Ban。",
        "ban_wait": "等待 {player} 的5秒 Ban 反应时间……",
        "ban_cancelled": "{player} 的 {card} 被 Ban 阻止。",
        "power_resolved": "Ban 时间结束，{player} 的 {card} 生效。",
        "ban_unavailable": "Ban 只能在对手的5秒反应时间内使用。",
        "chaos_title": "混沌卡",
        "chaos_good_free": "混沌效果：你的下一张 Power Card 不消耗行动点。",
        "chaos_good_score": "混沌效果：你获得2分。",
        "chaos_bad_score": "混沌效果：你失去2分。",
        "chaos_bad_double": "混沌效果：你的下一张 Power Card 消耗双倍行动点。",
        "chaos_neutral_peek": "混沌效果：你可以查看下一张牌但不抽走。",
        "chaos_status_free": "✨ 混沌效果生效：你的下一张 Power Card 不消耗行动点。",
        "chaos_status_double": "⚠️ 混沌效果生效：你的下一张 Power Card 消耗双倍行动点。",
        "chaos_status_peek": "👁️ 混沌效果生效：你可以查看下一张牌但不抽走。",
        "draw_number": "{player} 抽到数字牌 [{value}-{color}]，进入暂存区。",
        "draw_power": "{player} 抽到 Power Card [{card}]。",
        "draw_chaos": "{player} 抽到混沌卡。",
        "game_start": "🎮 游戏开始！碳对决启动，玩家1先手。",
        "end_turn_log": "回合结束：现在轮到 {player}。",
        "neutral_log": "{player} 中和了混色配对 {value}：0分。",
        "black_pair": "{player} 得到黑色配对 {value}：{points}分。",
        "red_pair": "{player} 得到红色配对 {value}：{points}分。",
        "plus_ap": "{player} 使用 +1 AP，获得1行动点。",
        "steal_staging_prepare": "{player} 正在选择对手暂存区的牌进行偷取。",
        "steal_staging_done": "{player} 从对手暂存区偷取了 {card}。",
        "single_swap_prepare": "{player} 正在准备单卡交换。",
        "single_swap_locked": "{player} 选择了 {card} 进行单卡交换。",
        "single_swap_done": "{player} 将 {own} 与 {target} 交换。",
        "push_prepare": "{player} 正在准备推送。",
        "push_done": "{player} 将 {card} 推给了对手。",
        "steal_prepare": "{player} 正在准备偷取。",
        "steal_done": "{player} 从对手手牌偷取了 Power Card [{card}]。",
        "destroy_prepare": "{player} 正在准备销毁。",
        "destroy_done": "{player} 销毁了对手的卡牌 [{card}]。",
        "all_swap_removed": "暂存区偷取",
        "reshuffle_done": "{player} 重新洗牌了剩余牌堆。",
        "peek_done": "{player} 使用了透视下一张牌。",
        "game_over": "最终结算：玩家1 {p1} 分，玩家2 {p2} 分。获胜者：{winner}。",
        "room_profession_locked": "本房间职业已锁定：{profession}。",
        "waiting_profession": "等待另一位玩家选择职业。",
        "auditor_start": "碳审计员开局获得两张透视下一张牌。",
    },
    "BM": {
        "page_title": "🃏 Carbon Match: Pertarungan Karbon",
        "room_caption": "Masukkan kod bilik yang sama dengan lawan, pilih peranan dan profesion, kemudian bertarung dalam talian.",
        "room_input_label": "Kod Bilik",
        "you_are": "Anda ialah",
        "profession_label": "Pilih profesion",
        "join_create": "Sertai / Cipta Bilik",
        "room_warn": "Sila masukkan kod bilik dahulu.",
        "leave_room": "🚪 Keluar Bilik",
        "room_header": "Bilik: {room} ｜ Anda: {player} ｜ Profesion: {profession}",
        "deck_status": "📦 Status Dek",
        "cards_remaining": "Kad Berbaki: {count} / 60",
        "current_turn": "📍 Giliran Semasa",
        "current_ap": "⚡ AP Semasa",
        "score_label": "⭐ Skor",
        "restart": "🔄 Mulakan Semula Permainan",
        "game_settled": "PERMAINAN SELESAI",
        "game_over_msg": "{winner} menang dengan {score} mata!",
        "p1_zone": "🔵 Zon Pemain 1",
        "p2_zone": "🔴 Zon Pemain 2",
        "you_suffix": " (Anda)",
        "your_turn": "⚡ Giliran anda (AP berbaki: {ap})",
        "opp_turn": "⏳ Giliran lawan, sila tunggu...",
        "current_score": "Skor Semasa: {score}",
        "profession_display": "Profesion: {profession}",
        "draw_card": "🎴 Ambil Kad (-1 AP)",
        "neutralize": "🌿 Neutralisasi (0 mata)",
        "end_turn": "⏭️ Tamatkan Giliran",
        "draw_warn": "AP tidak mencukupi atau dek sudah kosong.",
        "neutral_warn_no_pair": "Tiada kad warna berlawanan yang boleh dipasangkan.",
        "neutral_warn_few": "Zon sementara mempunyai kurang daripada 2 kad.",
        "hand_title": "🎒 Kad Tangan {player}",
        "hand_empty": "Tangan kosong",
        "staging_title": "📥 Zon Sementara {player}",
        "staging_empty": "Zon sementara kosong",
        "scored_title": "🏆 Zon Skor {player} (Jumlah Skor: {score})",
        "scored_empty": "Belum ada pasangan dalam zon skor",
        "pair_label": "Pasangan #{number}",
        "push_hint": "👉 Push aktif: pilih satu kad daripada zon sementara ini.",
        "single_swap_hint_own": "👉 Single Swap aktif: pilih kad daripada zon sementara anda.",
        "single_swap_hint_opp": "👉 Single Swap aktif: pilih kad daripada zon sementara lawan.",
        "steal_staging_hint": "👉 Steal Staging aktif: pilih kad daripada zon sementara lawan.",
        "steal_hint": "👉 Steal aktif: pilih Power Card lawan.",
        "destroy_hint": "👉 Destroy aktif: pilih satu kad daripada tangan lawan.",
        "ap_warn": "⚠️ AP tidak mencukupi.",
        "play_btn": "Mainkan #{number}",
        "push_btn": "Push #{number}",
        "select_btn": "Pilih #{number}",
        "swap_btn": "Tukar #{number}",
        "steal_btn": "Curi #{number}",
        "destroy_btn": "Musnahkan #{number}",
        "ban_btn": "🛑 Ban Power Card",
        "use_profession": "Gunakan Keupayaan Profesion",
        "profession_used": "Keupayaan profesion ini telah digunakan.",
        "regulator_ready": "Gunakan Emissions Regulator: Power Card lawan yang seterusnya memerlukan +1 AP.",
        "regulator_applied": "Emissions Regulator aktif: Power Card lawan yang seterusnya memerlukan +1 AP.",
        "regulator_debuff_active": "⚠️ Debuff aktif: Power Card anda yang seterusnya memerlukan +1 AP.",
        "peek_card": "Kad yang dilihat",
        "peek_empty": "Dek kosong, tiada kad seterusnya untuk dilihat.",
        "peek_note": "Hanya anda boleh melihat kad ini.",
        "ban_window": "{player} memainkan {card}. Anda mempunyai {seconds} saat untuk menggunakan Ban.",
        "ban_wait": "Menunggu tetingkap Ban 5 saat untuk {player}...",
        "ban_cancelled": "{card} milik {player} telah disekat oleh Ban.",
        "power_resolved": "Masa Ban tamat, {card} milik {player} telah dilaksanakan.",
        "ban_unavailable": "Ban hanya boleh digunakan dalam tetingkap tindak balas 5 saat lawan.",
        "chaos_title": "Kad Chaos",
        "chaos_good_free": "Kesan Chaos: Power Card anda yang seterusnya tidak memerlukan AP.",
        "chaos_good_score": "Kesan Chaos: anda mendapat 2 mata.",
        "chaos_bad_score": "Kesan Chaos: anda kehilangan 2 mata.",
        "chaos_bad_double": "Kesan Chaos: Power Card anda yang seterusnya memerlukan AP berganda.",
        "chaos_neutral_peek": "Kesan Chaos: anda boleh melihat kad seterusnya tanpa mengambilnya.",
        "chaos_status_free": "✨ Chaos aktif: Power Card anda yang seterusnya tidak memerlukan AP.",
        "chaos_status_double": "⚠️ Chaos aktif: Power Card anda yang seterusnya memerlukan AP berganda.",
        "chaos_status_peek": "👁️ Chaos aktif: anda boleh melihat kad seterusnya tanpa mengambilnya.",
        "draw_number": "{player} mengambil kad nombor [{value}-{color}] ke zon sementara.",
        "draw_power": "{player} mengambil Power Card [{card}].",
        "draw_chaos": "{player} mengambil Kad Chaos.",
        "game_start": "🎮 Permainan bermula! Carbon Match dimulakan. Pemain 1 bermula.",
        "end_turn_log": "Giliran tamat: sekarang giliran {player}.",
        "neutral_log": "{player} meneutralkan pasangan warna bercampur {value}: 0 mata.",
        "black_pair": "{player} mendapat pasangan hitam {value}: {points} mata.",
        "red_pair": "{player} mendapat pasangan merah {value}: {points} mata.",
        "plus_ap": "{player} menggunakan +1 AP dan mendapat 1 AP.",
        "steal_staging_prepare": "{player} sedang memilih kad daripada zon sementara lawan untuk dicuri.",
        "steal_staging_done": "{player} mencuri {card} daripada zon sementara lawan.",
        "single_swap_prepare": "{player} sedang menyediakan Single Swap.",
        "single_swap_locked": "{player} memilih {card} untuk Single Swap.",
        "single_swap_done": "{player} menukar {own} dengan {target}.",
        "push_prepare": "{player} sedang menyediakan Push.",
        "push_done": "{player} menolak {card} kepada lawan.",
        "steal_prepare": "{player} sedang menyediakan Steal.",
        "steal_done": "{player} mencuri Power Card [{card}] daripada tangan lawan.",
        "destroy_prepare": "{player} sedang menyediakan Destroy.",
        "destroy_done": "{player} memusnahkan kad lawan [{card}].",
        "all_swap_removed": "Steal Staging",
        "reshuffle_done": "{player} mengocok semula dek yang berbaki.",
        "peek_done": "{player} menggunakan Peek Next Card.",
        "game_over": "Keputusan akhir: Pemain 1 {p1} mata, Pemain 2 {p2} mata. Pemenang: {winner}.",
        "room_profession_locked": "Profesion bilik dikunci: {profession}.",
        "waiting_profession": "Menunggu pemain lain memilih profesion.",
        "auditor_start": "Carbon Auditor bermula dengan dua Peek Next Card.",
    },
}
# Language selector is intentionally kept in the new version.
if "language" not in st.session_state:
    st.session_state.language = "EN"

language_options = ["EN", "中文", "BM / Bahasa Malaysia"]

language_choice = st.selectbox(
    "🌐 Language / 语言 / Bahasa",
    options=language_options,
    index={"EN": 0, "ZH": 1, "BM": 2}.get(
        st.session_state.language,
        0,
    ),
    key="language_selector",
)

if language_choice == "EN":
    st.session_state.language = "EN"
elif language_choice == "中文":
    st.session_state.language = "ZH"
else:
    st.session_state.language = "BM"

LANG = st.session_state.language
T = LANG_TEXT[LANG]

# ============================================================
# Expandable Game Instructions
# ============================================================
if LANG == "EN":
    rules_title = "Game Instructions / Rules"
    rules_text = r"""
### Objective
Build your score by matching same-color number cards. The game ends when the deck is empty and neither player has a legal action left. The player with the higher score wins. A tied score is a draw.

### Turn Flow and AP
At the start of your turn, your base AP is reset to **2**. A Carbon Scientist starts each of their turns with **3 AP** instead. Draw a card for **1 AP**, play Power Cards according to their rules, use Neutralize on a same-number black/red pair for **0 points**, and press End Turn when finished. AP can go above the base amount during a turn.

### Number Cards and Scoring
A same-number red pair scores **number × 1.5** points. A same-number black pair scores **−number** points. A same-number black/red pair can be manually neutralized for **0 points**. Carbon Capture Engineer reduces the first black-pair loss by 2 points. Renewable Energy Engineer adds 2 points to the first red pair.

### Professions
| Profession | Effect |
|---|---|
| Carbon Scientist | Passive: every own turn starts with 3 AP. |
| Carbon Capture Engineer | Start-of-game buff: the first black-pair loss is reduced by 2. |
| Renewable Energy Engineer | Start-of-game buff: the first red pair gains 2 extra points. |
| Carbon Auditor | Starts with two Peek Next Card cards. Using Peek costs 0 AP. |
| Emissions Regulator | Once per game, manually apply a debuff to make the opponent's next Power Card cost 1 extra AP. |
| Ordinary Person | No additional effect. |

### Power Cards
- **+1 AP:** gain 1 AP; there are 6 copies.
- **Steal Staging:** steal one card from the opponent's staging area.
- **Single Swap:** select one of your staging cards and one opponent staging card, then exchange them.
- **Push:** move one card from your staging area to the opponent's staging area.
- **Steal:** take one Power Card from the opponent's hand.
- **Destroy:** remove one card from the opponent's hand.
- **Peek Next Card:** privately see the next deck card without drawing it. Carbon Auditor uses this for 0 AP.
- **Reshuffle:** shuffle the remaining deck.
- **Ban:** during the opponent's 5-second reaction window, cancel their Power Card. Ban itself has no AP cost.

### Chaos Card
A Chaos Card randomly gives one of five effects: your next Power Card costs 0 AP; gain 2 points; lose 2 points; your next Power Card costs double AP; or privately see the next card without drawing it.

### Ban Window
When a player uses a Power Card and the opponent has a Ban card, the opponent gets **5 seconds** to press Ban. If Ban is used, the Power Card is cancelled. If nobody uses Ban before the timer ends, the Power Card resolves.

### Victory
When the game settles, the higher final score wins. If both final scores are equal, the result is a draw. The victory BGM plays when the settlement banner appears.
"""
elif LANG == "ZH":
    rules_title = "游戏说明 / Rules"
    rules_text = r"""
### 游戏目标
通过配对同颜色数字牌获得分数。牌堆为空，并且双方都没有合法行动后，游戏结束。最终分数较高的玩家获胜；分数相同则为平局。

### 回合流程与行动点
每次轮到你时，基础行动点会重置为 **2 AP**。Carbon Scientist 每次自己的回合开始时拥有 **3 AP**。抽牌消耗 **1 AP**；Power Card 按各自规则使用；同编号黑红组合可以使用中和，获得 **0 分**；完成行动后按结束回合。回合内 AP 可以超过基础数量。

### 数字牌与分数计算
同编号红色配对获得 **数字 × 1.5** 分。同编号黑色配对获得 **−数字** 分。同编号黑红配对可以手动中和，获得 **0 分**。Carbon Capture Engineer 第一次黑色配对扣分减少2分。Renewable Energy Engineer 第一次红色配对额外获得2分。

### 职业
| 职业 | 效果 |
|---|---|
| Carbon Scientist / 碳科学家 | 被动效果：每次自己的回合开始时拥有3 AP。 |
| Carbon Capture Engineer / 碳捕集工程师 | 开局 Buff：第一次黑色配对的扣分减少2分。 |
| Renewable Energy Engineer / 可再生能源工程师 | 开局 Buff：第一次红色配对额外获得2分。 |
| Carbon Auditor / 碳审计员 | 开局获得两张 Peek Next Card；使用透视牌不消耗AP。 |
| Emissions Regulator / 排放监管员 | 每场一次，可以主动施加 Debuff，让对手下一张 Power Card 额外消耗1 AP。 |
| Ordinary Person / 普通人 | 没有额外效果。 |

### Power Card
- **+1 AP：** 获得1行动点，共6张。
- **Steal Staging：** 从对手暂存区偷取一张牌。
- **Single Swap：** 选择自己的暂存牌和对手的一张暂存牌，然后交换。
- **Push：** 把自己暂存区的一张牌推到对手暂存区。
- **Steal：** 从对手手牌偷取一张 Power Card。
- **Destroy：** 销毁对手手牌中的一张牌。
- **Peek Next Card：** 查看牌堆下一张牌但不抽走；Carbon Auditor 使用它不消耗AP。
- **Reshuffle：** 重新洗牌剩余牌堆。
- **Ban：** 在对手的5秒反应时间内取消对手的 Power Card；Ban 本身不消耗AP。

### Chaos Card
抽到 Chaos Card 后，会随机得到五种效果中的一种：下一张 Power Card 不消耗AP；获得2分；失去2分；下一张 Power Card 消耗双倍AP；或者查看牌堆下一张牌但不抽走。

### Ban 反应时间
当玩家使用 Power Card 且对手手里有 Ban 时，对手有 **5秒** 可以点击 Ban。如果使用 Ban，Power Card 会被取消；如果5秒内没有使用 Ban，Power Card 就会正常生效。

### 胜负
当游戏结算时，最终分数较高者获胜；分数相同则为平局。出现结算横幅时会播放胜利 BGM。
"""

elif LANG == "BM":
    rules_title = "Arahan Permainan / Peraturan"
    rules_text = r"""
### Objektif
Dapatkan mata dengan memadankan kad nombor yang mempunyai warna sama. Permainan tamat apabila dek kosong dan kedua-dua pemain tiada tindakan yang sah. Pemain dengan mata lebih tinggi menang. Jika mata sama, keputusan ialah seri.

### Giliran dan AP
Pada permulaan giliran anda, AP asas ditetapkan kepada **2 AP**. Carbon Scientist bermula setiap gilirannya dengan **3 AP**. Ambil kad menggunakan **1 AP**, gunakan Power Card mengikut peraturannya, dan tamatkan giliran selepas selesai. AP boleh melebihi jumlah asas.

### Pengiraan Mata
Pasangan merah dengan nombor yang sama mendapat **nombor × 1.5** mata. Pasangan hitam dengan nombor yang sama mendapat **−nombor** mata. Pasangan hitam dan merah dengan nombor yang sama boleh dineutralkan untuk **0 mata**.

Carbon Capture Engineer mengurangkan kehilangan daripada pasangan hitam pertama sebanyak 2 mata. Renewable Energy Engineer memberikan tambahan 2 mata untuk pasangan merah pertama.

### Profesion
| Profesion | Kesan |
|---|---|
| Carbon Scientist | Pasif: setiap giliran anda bermula dengan 3 AP. |
| Carbon Capture Engineer | Buff permulaan: kehilangan pasangan hitam pertama dikurangkan sebanyak 2 mata. |
| Renewable Energy Engineer | Buff permulaan: pasangan merah pertama mendapat tambahan 2 mata. |
| Carbon Auditor | Bermula dengan dua Peek Next Card. Kad Peek tidak menggunakan AP. |
| Emissions Regulator | Sekali setiap permainan, gunakan secara manual untuk menjadikan Power Card lawan yang seterusnya memerlukan +1 AP. |
| Ordinary Person | Tiada kesan tambahan. |

### Power Card
- **+1 AP:** Dapatkan 1 AP. Terdapat 6 kad.
- **Steal Staging:** Curi satu kad daripada zon sementara lawan.
- **Single Swap:** Tukar satu kad zon sementara anda dengan satu kad zon sementara lawan.
- **Push:** Pindahkan satu kad zon sementara anda ke zon sementara lawan.
- **Steal:** Curi satu Power Card daripada tangan lawan.
- **Destroy:** Musnahkan satu kad daripada tangan lawan.
- **Peek Next Card:** Lihat kad teratas dek tanpa mengambilnya.
- **Reshuffle:** Kocok semula baki dek.
- **Ban:** Batalkan Power Card lawan dalam tetingkap tindak balas 5 saat.

### Kad Chaos
Kad Chaos memilih satu daripada lima kesan secara rawak: Power Card seterusnya tidak memerlukan AP; dapat 2 mata; kehilangan 2 mata; Power Card seterusnya memerlukan AP berganda; atau lihat kad seterusnya tanpa mengambilnya.

### Tetingkap Ban
Apabila pemain menggunakan Power Card dan lawan mempunyai Ban, lawan mempunyai **5 saat** untuk menekan Ban. Jika Ban digunakan, Power Card dibatalkan. Jika tiada Ban digunakan sebelum masa tamat, Power Card dilaksanakan.

### Menang atau Seri
Apabila permainan selesai, pemain dengan jumlah mata akhir yang lebih tinggi menang. Jika jumlah mata akhir sama, keputusan ialah seri. Muzik kemenangan dimainkan apabila permainan selesai.
"""


with st.expander(f"❗ {rules_title}", expanded=False):
    st.markdown(rules_text)

PROFESSION_KEYS = [
    "Carbon Scientist",
    "Carbon Capture Engineer",
    "Renewable Energy Engineer",
    "Carbon Auditor",
    "Emissions Regulator",
    "Ordinary Person",
]

PROFESSION_LABELS = {
    "EN": {
        "Carbon Scientist": "Carbon Scientist",
        "Carbon Capture Engineer": "Carbon Capture Engineer",
        "Renewable Energy Engineer": "Renewable Energy Engineer",
        "Carbon Auditor": "Carbon Auditor",
        "Emissions Regulator": "Emissions Regulator",
        "Ordinary Person": "Ordinary Person",
    },
    "ZH": {
        "Carbon Scientist": "碳科学家",
        "Carbon Capture Engineer": "碳捕集工程师",
        "Renewable Energy Engineer": "可再生能源工程师",
        "Carbon Auditor": "碳审计员",
        "Emissions Regulator": "排放监管员",
        "Ordinary Person": "普通人",
    },
        "BM": {
        "Carbon Scientist": "Saintis Karbon",
        "Carbon Capture Engineer": "Jurutera Penangkapan Karbon",
        "Renewable Energy Engineer": "Jurutera Tenaga Boleh Baharu",
        "Carbon Auditor": "Juruaudit Karbon",
        "Emissions Regulator": "Pengawal Selia Pelepasan",
        "Ordinary Person": "Orang Biasa",
    },

}

PROFESSION_DESCRIPTIONS = {
    "EN": {
        "Carbon Scientist": "Passive: your turn starts with 3 AP.",
        "Carbon Capture Engineer": "Start-of-game buff: reduce the first black-pair loss by 2 points.",
        "Renewable Energy Engineer": "Start-of-game buff: the first red pair gains +2 points.",
        "Carbon Auditor": "Start with two Peek Next Cards. Your Peek cards cost 0 AP.",
        "Emissions Regulator": "Once per game, apply a debuff so the opponent's next Power Card costs +1 AP.",
        "Ordinary Person": "No additional effect.",
    },
    "ZH": {
        "Carbon Scientist": "被动：你的回合开始时拥有3行动点。",
        "Carbon Capture Engineer": "开局 Buff：第一次黑色配对的扣分减少2分。",
        "Renewable Energy Engineer": "开局 Buff：第一次红色配对额外获得2分。",
        "Carbon Auditor": "开局获得两张透视下一张牌；使用透视牌不消耗行动点。",
        "Emissions Regulator": "每场一次主动施加 Debuff，让对手下一张 Power Card 额外消耗1行动点。",
        "Ordinary Person": "没有额外效果。",
    },
        "BM": {
        "Carbon Scientist": "Pasif: setiap giliran anda bermula dengan 3 AP.",
        "Carbon Capture Engineer": "Buff permulaan: kehilangan daripada pasangan hitam pertama dikurangkan sebanyak 2 mata.",
        "Renewable Energy Engineer": "Buff permulaan: pasangan merah pertama mendapat tambahan 2 mata.",
        "Carbon Auditor": "Bermula dengan dua Peek Next Card. Kad Peek tidak menggunakan AP.",
        "Emissions Regulator": "Sekali setiap permainan, gunakan secara manual untuk menjadikan Power Card lawan yang seterusnya memerlukan +1 AP.",
        "Ordinary Person": "Tiada kesan tambahan.",
    },
}

POWER_CARDS = {
    "+1 AP",
    "Steal Staging",
    "Single Swap",
    "Push",
    "Steal",
    "Destroy",
    "Peek Next Card",
    "Reshuffle",
    "Ban",
}

TACTICAL_CARDS = {"Steal Staging", "Single Swap", "Push", "Steal", "Destroy"}


# ============================================================
# Audio Helpers
# ============================================================
AUDIO_DIR = Path(__file__).parent / "assets"
BUTTON_SFX_PATH = AUDIO_DIR / "sfx" / "button-click.mp3"
POWER_SFX_PATH = AUDIO_DIR / "sfx" / "power-card.mp3"
VICTORY_BGM_PATH = AUDIO_DIR / "sfx" / "victory.mp3"


def audio_data_uri(path: Path) -> str:
    if not path.exists():
        return ""
    mime_type = mimetypes.guess_type(path.name)[0] or "audio/mpeg"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def install_game_audio():
    """Install one delegated listener for normal and Power Card button sounds."""
    click_uri = audio_data_uri(BUTTON_SFX_PATH)
    power_uri = audio_data_uri(POWER_SFX_PATH)
    victory_uri = audio_data_uri(VICTORY_BGM_PATH)

    if not click_uri:
        st.warning("Missing assets/sfx/button-click.mp3")
        return

    audio_html = """
    <script>
    (() => {
        const hostWindow = window.parent || window;
        const hostDocument = hostWindow.document;
        const clickSrc = __CLICK_SRC__;
        const powerSrc = __POWER_SRC__;
        const victorySrc = __VICTORY_SRC__;

        if (hostWindow.__carbonMatchAudio) return;

        const clickAudio = clickSrc ? new hostWindow.Audio(clickSrc) : null;
        const powerAudio = powerSrc ? new hostWindow.Audio(powerSrc) : null;
        const victoryAudio = victorySrc ? new hostWindow.Audio(victorySrc) : null;
        if (clickAudio) {
            clickAudio.preload = "auto";
            clickAudio.volume = 0.55;
        }
        if (powerAudio) {
            powerAudio.preload = "auto";
            powerAudio.volume = 0.70;
        }
        if (victoryAudio) {
            victoryAudio.preload = "auto";
            victoryAudio.volume = 0.80;
        }

        function safePlay(audio) {
            if (!audio) return;
            const promise = audio.play();
            if (promise && promise.catch) promise.catch(() => {});
        }

        function playClickSound() {
            if (!clickAudio) return;
            clickAudio.currentTime = 0;
            safePlay(clickAudio);
        }

        function playPowerSound() {
            if (!powerAudio) return;
            powerAudio.currentTime = 0;
            safePlay(powerAudio);
        }

        function playButtonSound(button) {
            const text = button.innerText || "";
            if (text.includes("⚡") || text.includes("🛑")) {
                playPowerSound();
            } else {
                playClickSound();
            }
        }

        function playVictoryMusic() {
            if (!victoryAudio || hostWindow.__carbonMatchVictoryPlayed) return;
            hostWindow.__carbonMatchVictoryPlayed = true;
            hostDocument.querySelectorAll("audio").forEach((audio) => {
                if (audio !== victoryAudio) {
                    audio.pause();
                    audio.currentTime = 0;
                }
            });
            victoryAudio.currentTime = 0;
            safePlay(victoryAudio);
        }

        function handlePointer(event) {
            const button = event.target.closest?.("button");
            if (button) playButtonSound(button);
        }

        function handleKeyboard(event) {
            if (event.key !== "Enter" && event.key !== " ") return;
            const button = event.target.closest?.("button");
            if (button) playButtonSound(button);
        }

        hostDocument.addEventListener("pointerdown", handlePointer, true);
        hostDocument.addEventListener("keydown", handleKeyboard, true);
        hostWindow.__carbonMatchAudio = { playVictoryMusic };
    })();
    </script>
    """
    audio_html = audio_html.replace("__CLICK_SRC__", json.dumps(click_uri))
    audio_html = audio_html.replace("__POWER_SRC__", json.dumps(power_uri))
    audio_html = audio_html.replace("__VICTORY_SRC__", json.dumps(victory_uri))
    components.html(audio_html, height=0, width=0)


# ============================================================
# Utility Functions
# ============================================================
LOG_KEYS = {
    "game_start",
    "end_turn_log",
    "neutral_log",
    "black_pair",
    "red_pair",
    "plus_ap",
    "steal_staging_prepare",
    "steal_staging_done",
    "single_swap_prepare",
    "single_swap_locked",
    "single_swap_done",
    "push_prepare",
    "push_done",
    "steal_prepare",
    "steal_done",
    "destroy_prepare",
    "destroy_done",
    "reshuffle_done",
    "peek_done",
    "game_over",
    "room_profession_locked",
    "auditor_start",
    "draw_number",
    "draw_power",
    "draw_chaos",
    "ban_cancelled",
    "power_resolved",
    "regulator_applied",
    "chaos_good_free",
    "chaos_good_score",
    "chaos_bad_score",
    "chaos_bad_double",
    "chaos_neutral_peek",
}

def tr(key: str, **kwargs) -> str:
    return T[key].format(**kwargs)


def display_profession(key):
    return PROFESSION_LABELS[LANG].get(key, key or "Not selected")


def display_player(is_p1):
    return "Player 1" if is_p1 else "Player 2"


def hand_for(state, is_p1):
    return state["p1_hand"] if is_p1 else state["p2_hand"]


def staging_for(state, is_p1):
    return state["p1_staging"] if is_p1 else state["p2_staging"]


def scoring_for(state, is_p1):
    return state["p1_scoring"] if is_p1 else state["p2_scoring"]


def score_for(state, is_p1):
    return state["p1_score"] if is_p1 else state["p2_score"]


def set_score(state, is_p1, value):
    if is_p1:
        state["p1_score"] = value
    else:
        state["p2_score"] = value


def profession_for(state, is_p1):
    return state["p1_profession"] if is_p1 else state["p2_profession"]


def base_ap_for(state, is_p1):
    return 3 if profession_for(state, is_p1) == "Carbon Scientist" else 2


def set_turn_ap(state, is_p1):
    state["ap"] = base_ap_for(state, is_p1)


def add_log(state, message):
    state["logs"].insert(0, message)
    if len(state["logs"]) > 2000:
        state["logs"].pop()


def clear_tactical_state(state):
    state["active_tactical"] = None
    state["tactical_player"] = None
    state["q_selected_own_card"] = None


def card_is_power(card):
    return len(card) >= 2 and card[1] == "T"


def card_text(card):
    return str(card[0])


# ============================================================
# Deck and Card Rendering
# ============================================================
def new_deck():
    deck = []

    # Numbers 1, 2, 3: four black and four red copies each.
    for number in range(1, 4):
        for _ in range(4):
            deck.append([str(number), "B"])
            deck.append([str(number), "R"])

    # Number 4: two black and two red copies.
    for _ in range(2):
        deck.append(["4", "B"])
        deck.append(["4", "R"])

    # +1 AP remains at six copies.
    for _ in range(6):
        deck.append(["+1 AP", "T"])

    # All other Power Cards are three copies each.
    for _ in range(3):
        for card_name in [
            "Steal Staging",
            "Single Swap",
            "Push",
            "Steal",
            "Destroy",
            "Peek Next Card",
            "Reshuffle",
            "Ban",
        ]:
            deck.append([card_name, "T"])

    # Chaos/Joker remains at two copies.
    for _ in range(2):
        deck.append(["Chaos Card", "C"])

    random.shuffle(deck)
    return deck


def render_card_html(value, card_type, size="normal"):
    palette = {
        "+1 AP": ("#e3f2fd", "#2196f3", "#0d47a1", "Action Point"),
        "Steal Staging": ("#f3e5f5", "#ab47bc", "#4a148c", "Staging Steal"),
        "Single Swap": ("#e1f5fe", "#00acc1", "#006064", "Target Swap"),
        "Push": ("#e8f5e9", "#4caf50", "#1b5e20", "Card Push"),
        "Steal": ("#fff3cd", "#ffc107", "#856404", "Steal Card"),
        "Destroy": ("#f8d7da", "#dc3545", "#721c24", "Destroy Card"),
        "Peek Next Card": ("#e8eaf6", "#3f51b5", "#1a237e", "Peek Card"),
        "Reshuffle": ("#ede7f6", "#673ab7", "#311b92", "Reshuffle"),
        "Ban": ("#eceff1", "#455a64", "#263238", "Counter Card"),
        "Chaos Card": ("#fff3e0", "#ff9800", "#e65100", "Chaos Event"),
    }
    if value in palette:
        bg, border, text_color, label = palette[value]
    elif card_type == "B":
        bg, border, text_color, label = "#f0f2f6", "#333333", "#111111", "Emission"
    elif card_type == "R":
        bg, border, text_color, label = "#ffe6e6", "#ff4b4b", "#c62828", "Capture"
    else:
        bg, border, text_color, label = "#ffffff", "#cccccc", "#333333", ""

    if size == "large":
        width, height, font_size, label_size = "100px", "130px", "18px", "11px"
    elif size == "medium":
        width, height, font_size, label_size = "75px", "95px", "14px", "10px"
    else:
        width, height, font_size, label_size = "55px", "70px", "10px", "8px"

    safe_value = html.escape(str(value))
    return f"""
    <div style="width:{width};height:{height};border:3px solid {border};border-radius:10px;
                background-color:{bg};display:inline-flex;flex-direction:column;
                align-items:center;justify-content:center;box-shadow:2px 3px 6px rgba(0,0,0,0.15);
                margin:4px;text-align:center;padding:2px;">
        <span style="font-size:{font_size};font-weight:bold;color:{text_color};word-break:break-word;">{safe_value}</span>
        <span style="font-size:{label_size};color:#444;font-weight:bold;margin-top:2px;">{label}</span>
    </div>
    """


# ============================================================
# State and Supabase
# ============================================================
def initial_state(lang="EN"):
    return {
        "rules_version": RULES_VERSION,
        "deck": new_deck(),
        "ap": 2,
        "turn": "Player 1",
        "p1_profession": None,
        "p2_profession": None,
        "p1_staging": [],
        "p1_scoring": [],
        "p1_hand": [],
        "p1_score": 0.0,
        "p2_staging": [],
        "p2_scoring": [],
        "p2_hand": [],
        "p2_score": 0.0,
        "p1_capture_shield": False,
        "p2_capture_shield": False,
        "p1_renewable_bonus": False,
        "p2_renewable_bonus": False,
        "p1_emissions_used": False,
        "p2_emissions_used": False,
        "p1_emissions_debuff": False,
        "p2_emissions_debuff": False,
        "p1_emissions_remaining": 2,
        "p2_emissions_remaining": 2,
        "p1_free_power_remaining": 0,
        "p2_free_power_remaining": 0,
        "p1_double_power_next": False,
        "p2_double_power_next": False,
        "p1_auditor_cards_given": False,
        "p2_auditor_cards_given": False,
        "p1_peeked_card": None,
        "p2_peeked_card": None,
        "active_tactical": None,
        "tactical_player": None,
        "q_selected_own_card": None,
        "pending_power": None,
        "game_over": False,
        "restart_requested": False,
        "restart_p1_profession": None,
        "restart_p2_profession": None,
        "logs": [LANG_TEXT[lang]["game_start"]],
    }


def load_game(room_code):
    result = supabase.table(TABLE).select("*").eq("room_code", room_code).execute()
    if result.data:
        state = result.data[0]["state"]
        if state.get("rules_version") != RULES_VERSION:
            state = initial_state(LANG)
            supabase.table(TABLE).update({"state": state}).eq("room_code", room_code).execute()
        return state

    state = initial_state(LANG)
    supabase.table(TABLE).insert({"room_code": room_code, "state": state}).execute()
    return state


def save_game(room_code, state):
    supabase.table(TABLE).update({"state": state}).eq("room_code", room_code).execute()


def give_auditor_cards(state, is_p1):
    flag = "p1_auditor_cards_given" if is_p1 else "p2_auditor_cards_given"
    if state[flag]:
        return
    # These are profession-granted cards, not removed from the shared deck.
    # This lets both players choose Carbon Auditor and still receive two cards.
    hand_for(state, is_p1).extend([
        ["Peek Next Card", "T"],
        ["Peek Next Card", "T"],
    ])
    state[flag] = True
    add_log(state, tr("auditor_start"))


def apply_starting_profession(state, is_p1):
    profession = profession_for(state, is_p1)
    if profession == "Carbon Capture Engineer":
        state["p1_capture_shield" if is_p1 else "p2_capture_shield"] = True
    elif profession == "Renewable Energy Engineer":
        state["p1_renewable_bonus" if is_p1 else "p2_renewable_bonus"] = True
    elif profession == "Carbon Auditor":
        give_auditor_cards(state, is_p1)


def register_profession(state, is_p1, profession):
    key = "p1_profession" if is_p1 else "p2_profession"
    if state[key] is not None:
        return False

    state[key] = profession
    apply_starting_profession(state, is_p1)
    if state["turn"] == display_player(is_p1):
        set_turn_ap(state, is_p1)
    add_log(state, tr("room_profession_locked", profession=display_profession(profession)))
    return True


def restart_with_selected_professions(p1_profession, p2_profession):
    new_state = initial_state(LANG)
    new_state["p1_profession"] = p1_profession
    new_state["p2_profession"] = p2_profession

    if p1_profession:
        apply_starting_profession(new_state, True)
    if p2_profession:
        apply_starting_profession(new_state, False)

    # Player 1 starts the new round.
    set_turn_ap(new_state, True)
    return new_state


# ============================================================
# Scoring and Game-Over Helpers
# ============================================================
def pair_score(card_pair):
    total = 0.0
    for card in card_pair:
        if len(card) < 2:
            continue
        try:
            number = int(card[0])
        except (ValueError, TypeError):
            continue
        total += -number if card[1] == "B" else number * 1.5
    return total


def score_same_color_pair(state, is_p1, value, color, cards):
    number = int(value)
    if color == "B":
        points = -float(number)
        shield_key = "p1_capture_shield" if is_p1 else "p2_capture_shield"
        if state[shield_key]:
            points = min(0.0, points + 2.0)
            state[shield_key] = False
    else:
        points = number * 1.5
        bonus_key = "p1_renewable_bonus" if is_p1 else "p2_renewable_bonus"
        if state[bonus_key]:
            points += 2.0
            state[bonus_key] = False

    set_score(state, is_p1, score_for(state, is_p1) + points)
    scoring_for(state, is_p1).append(cards)
    if color == "B":
        add_log(state, tr("black_pair", player=display_player(is_p1), value=value, points=points))
    else:
        add_log(state, tr("red_pair", player=display_player(is_p1), value=value, points=points))


def auto_score_same_color_pairs(state, is_p1):
    staging = staging_for(state, is_p1)
    changed = False
    while True:
        found = False
        values = sorted({card[0] for card in staging if len(card) >= 2 and card[1] in ["B", "R"]})
        for value in values:
            for color in ["B", "R"]:
                matching = [card for card in staging if card[0] == value and card[1] == color]
                if len(matching) >= 2:
                    pair = [matching[0], matching[1]]
                    staging.remove(matching[0])
                    staging.remove(matching[1])
                    score_same_color_pair(state, is_p1, value, color, pair)
                    found = True
                    changed = True
                    break
            if found:
                break
        if not found:
            break
    return changed


def has_mixed_color_pair(staging):
    values = {}
    for card in staging:
        if len(card) >= 2 and card[1] in ["B", "R"]:
            values.setdefault(card[0], set()).add(card[1])
    return any(colors == {"B", "R"} for colors in values.values())


def neutralize_first_mixed_pair(state, is_p1):
    staging = staging_for(state, is_p1)
    if len(staging) < 2:
        return False
    for value in sorted({card[0] for card in staging if card[1] in ["B", "R"]}):
        black = next((card for card in staging if card[0] == value and card[1] == "B"), None)
        red = next((card for card in staging if card[0] == value and card[1] == "R"), None)
        if black and red:
            staging.remove(black)
            staging.remove(red)
            scoring_for(state, is_p1).append([black, red])
            add_log(state, tr("neutral_log", player=display_player(is_p1), value=value))
            return True
    return False


def has_valid_tactical_target(state):
    active = state.get("active_tactical")
    actor = state.get("tactical_player")
    if active is None or actor is None:
        return False
    own_staging = staging_for(state, actor)
    opponent_staging = staging_for(state, not actor)
    opponent_hand = hand_for(state, not actor)
    if active in ["Steal Staging", "Single Swap"]:
        if active == "Single Swap" and state.get("q_selected_own_card") is None:
            return len(own_staging) > 0
        return len(opponent_staging) > 0
    if active == "Push":
        return len(own_staging) > 0
    if active == "Steal":
        return any(card_is_power(card) for card in opponent_hand)
    if active == "Destroy":
        return len(opponent_hand) > 0
    return False


def has_progress_action(state, is_p1):
    if state.get("pending_power") is not None or state.get("active_tactical") is not None:
        return True
    if len(state["deck"]) > 0:
        return True
    hand = hand_for(state, is_p1)
    own_staging = staging_for(state, is_p1)
    opponent_staging = staging_for(state, not is_p1)
    opponent_hand = hand_for(state, not is_p1)
    if has_mixed_color_pair(own_staging):
        return True
    if any(card[0] == "+1 AP" for card in hand):
        return True
    # A normal Power Card needs 1 AP. A Chaos free-Power effect can make
    # the next one legal even when the current AP is 0.
    free_power = state["p1_free_power_remaining" if is_p1 else "p2_free_power_remaining"] > 0
    can_pay_power = state["ap"] > 0 or free_power
    if can_pay_power and any(card[0] == "Steal Staging" for card in hand) and opponent_staging:
        return True
    if can_pay_power and any(card[0] == "Single Swap" for card in hand) and own_staging and opponent_staging:
        return True
    if can_pay_power and any(card[0] == "Push" for card in hand) and own_staging:
        return True
    if can_pay_power and any(card[0] == "Steal" for card in hand) and any(card_is_power(card) for card in opponent_hand):
        return True
    if can_pay_power and any(card[0] == "Destroy" for card in hand) and opponent_hand:
        return True
    if can_pay_power and any(card[0] in ["Peek Next Card", "Reshuffle"] for card in hand) and state["deck"]:
        return True
    if profession_for(state, is_p1) == "Emissions Regulator":
        used_key = "p1_emissions_used" if is_p1 else "p2_emissions_used"
        if not state[used_key] and any(card_is_power(card) for card in opponent_hand):
            return True
    return False


def check_game_over_and_settle(state):
    if state.get("game_over", False):
        return False
    if state.get("active_tactical") is not None and not has_valid_tactical_target(state):
        clear_tactical_state(state)
    if state.get("pending_power") is not None or state.get("active_tactical") is not None:
        return False
    if len(state["deck"]) > 0:
        return False
    if has_progress_action(state, True) or has_progress_action(state, False):
        return False

    state["game_over"] = True
    p1_score = state["p1_score"]
    p2_score = state["p2_score"]
    if p1_score > p2_score:
        winner = display_player(True)
    elif p2_score > p1_score:
        winner = display_player(False)
    else:
        winner = "Draw"
    add_log(state, tr("game_over", p1=p1_score, p2=p2_score, winner=winner))
    return True


# ============================================================
# Power Cards, Chaos, and Ban Reaction
# ============================================================
def power_card_cost(state, actor_is_p1, card_name):
    # +1 AP normally costs 0. All other Power Cards normally cost 1.
    # Carbon Auditor's Peek Next Card also costs 0 AP.
    base_cost = 0 if card_name == "+1 AP" else 1
    auditor_free_peek = (
        profession_for(state, actor_is_p1) == "Carbon Auditor"
        and card_name == "Peek Next Card"
    )
    if auditor_free_peek:
        base_cost = 0

    free_key = "p1_free_power_remaining" if actor_is_p1 else "p2_free_power_remaining"
    double_key = "p1_double_power_next" if actor_is_p1 else "p2_double_power_next"
    debuff_key = "p1_emissions_debuff" if actor_is_p1 else "p2_emissions_debuff"

    free_effect = state[free_key] > 0
    double_effect = state[double_key]
    regulator_effect = state[debuff_key]

    # Carbon Auditor's Peek is always free. It still consumes any pending
    # one-shot modifier because Peek is the next Power Card used.
    if auditor_free_peek:
        if free_effect:
            state[free_key] = max(0, state[free_key] - 1)
        if double_effect:
            state[double_key] = False
        if regulator_effect:
            state[debuff_key] = False
        return 0

    if free_effect:
        cost = 0
    else:
        cost = base_cost
    if double_effect:
        cost *= 2
    if regulator_effect:
        cost += 1


    # Any pending Chaos/Regulator effect applies to the next Power Card.
    if free_effect:
        state[free_key] = max(0, state[free_key] - 1)
    if double_effect:
        state[double_key] = False
    if regulator_effect:
        state[debuff_key] = False
    return cost


def opponent_has_ban(state, actor_is_p1):
    return any(card[0] == "Ban" for card in hand_for(state, not actor_is_p1))


def start_power_card(state, actor_is_p1, hand_index):
    hand = hand_for(state, actor_is_p1)
    if hand_index < 0 or hand_index >= len(hand):
        return False, "Invalid card selection."
    card = hand[hand_index]
    card_name = card[0]
    if card_name == "Ban":
        return False, tr("ban_unavailable")
    if card_name not in POWER_CARDS:
        return False, "This is not a Power Card."

    cost = power_card_cost(state, actor_is_p1, card_name)
    if state["ap"] < cost:
        return False, tr("ap_warn")

    hand.pop(hand_index)
    state["ap"] -= cost
    if opponent_has_ban(state, actor_is_p1):
        state["pending_power"] = {
            "actor_is_p1": actor_is_p1,
            "card": card,
            "deadline": time.time() + 5,
        }
        return True, None

    execute_power_card(state, actor_is_p1, card)
    return True, None


def execute_power_card(state, actor_is_p1, card):
    card_name = card[0]
    actor_name = display_player(actor_is_p1)
    hand = hand_for(state, actor_is_p1)

    if card_name == "+1 AP":
        state["ap"] += 1
        add_log(state, tr("plus_ap", player=actor_name))
    elif card_name == "Steal Staging":
        state["active_tactical"] = "Steal Staging"
        state["tactical_player"] = actor_is_p1
        add_log(state, tr("steal_staging_prepare", player=actor_name))
    elif card_name == "Single Swap":
        state["active_tactical"] = "Single Swap"
        state["tactical_player"] = actor_is_p1
        state["q_selected_own_card"] = None
        add_log(state, tr("single_swap_prepare", player=actor_name))
    elif card_name == "Push":
        state["active_tactical"] = "Push"
        state["tactical_player"] = actor_is_p1
        add_log(state, tr("push_prepare", player=actor_name))
    elif card_name == "Steal":
        state["active_tactical"] = "Steal"
        state["tactical_player"] = actor_is_p1
        add_log(state, tr("steal_prepare", player=actor_name))
    elif card_name == "Destroy":
        state["active_tactical"] = "Destroy"
        state["tactical_player"] = actor_is_p1
        add_log(state, tr("destroy_prepare", player=actor_name))
    elif card_name == "Peek Next Card":
        if state["deck"]:
            key = "p1_peeked_card" if actor_is_p1 else "p2_peeked_card"
            state[key] = list(state["deck"][0])
            add_log(state, tr("peek_done", player=actor_name))
        else:
            add_log(state, tr("peek_empty"))
    elif card_name == "Reshuffle":
        random.shuffle(state["deck"])
        add_log(state, tr("reshuffle_done", player=actor_name))


def resolve_pending_power(state):
    pending = state.get("pending_power")
    if not pending:
        return False
    if time.time() < pending["deadline"]:
        return False
    actor_is_p1 = pending["actor_is_p1"]
    card = pending["card"]
    state["pending_power"] = None
    execute_power_card(state, actor_is_p1, card)
    add_log(state, tr("power_resolved", player=display_player(actor_is_p1), card=card[0]))
    return True


def cancel_pending_power_with_ban(state, defender_is_p1):
    pending = state.get("pending_power")

    # There must be an opponent's Power Card waiting for Ban.
    if not isinstance(pending, dict):
        return False

    if pending.get("actor_is_p1") == defender_is_p1:
        return False

    defender_hand = hand_for(state, defender_is_p1)
    ban_index = next(
        (
            index
            for index, card in enumerate(defender_hand)
            if card[0] == "Ban"
        ),
        None,
    )

    if ban_index is None:
        return False

    actor_is_p1 = pending["actor_is_p1"]
    card_name = pending["card"][0]

    # Remove Ban from the defender's hand.
    defender_hand.pop(ban_index)

    # Cancel the opponent's waiting Power Card.
    state["pending_power"] = None

    add_log(
        state,
        tr(
            "ban_cancelled",
            player=display_player(actor_is_p1),
            card=card_name,
        ),
    )
    return True



def apply_chaos(state, actor_is_p1):
    actor_name = display_player(actor_is_p1)
    effect = random.choice([
        "good_free",
        "good_score",
        "bad_score",
        "bad_double",
        "neutral_peek",
    ])
    if effect == "good_free":
        key = "p1_free_power_remaining" if actor_is_p1 else "p2_free_power_remaining"
        state[key] += 1
        add_log(state, tr("chaos_good_free"))
    elif effect == "good_score":
        set_score(state, actor_is_p1, score_for(state, actor_is_p1) + 2)
        add_log(state, tr("chaos_good_score"))
    elif effect == "bad_score":
        set_score(state, actor_is_p1, score_for(state, actor_is_p1) - 2)
        add_log(state, tr("chaos_bad_score"))
    elif effect == "bad_double":
        key = "p1_double_power_next" if actor_is_p1 else "p2_double_power_next"
        state[key] = True
        add_log(state, tr("chaos_bad_double"))
    else:
        key = "p1_peeked_card" if actor_is_p1 else "p2_peeked_card"
        state[key] = list(state["deck"][0]) if state["deck"] else None
        add_log(state, tr("chaos_neutral_peek"))
    return effect


# ============================================================
# Card Action Completion
# ============================================================
def complete_steal_staging(state, actor_is_p1, target_index):
    opponent_staging = staging_for(state, not actor_is_p1)
    own_staging = staging_for(state, actor_is_p1)
    if target_index >= len(opponent_staging):
        return False
    card = opponent_staging.pop(target_index)
    own_staging.append(card)
    add_log(state, tr("steal_staging_done", player=display_player(actor_is_p1), card=card[0]))
    auto_score_same_color_pairs(state, actor_is_p1)
    clear_tactical_state(state)
    return True


def complete_push(state, actor_is_p1, target_index):
    own_staging = staging_for(state, actor_is_p1)
    opponent_staging = staging_for(state, not actor_is_p1)
    if target_index >= len(own_staging):
        return False
    card = own_staging.pop(target_index)
    opponent_staging.append(card)
    add_log(state, tr("push_done", player=display_player(actor_is_p1), card=card[0]))
    auto_score_same_color_pairs(state, not actor_is_p1)
    clear_tactical_state(state)
    return True


def complete_single_swap(state, actor_is_p1, target_index):
    selected = state.get("q_selected_own_card")
    if selected is None:
        own_staging = staging_for(state, actor_is_p1)
        if target_index >= len(own_staging):
            return False
        state["q_selected_own_card"] = [target_index, list(own_staging[target_index])]
        add_log(state, tr("single_swap_locked", player=display_player(actor_is_p1), card=own_staging[target_index][0]))
        return True

    own_index, own_card = selected
    own_staging = staging_for(state, actor_is_p1)
    opponent_staging = staging_for(state, not actor_is_p1)
    if own_index >= len(own_staging) or target_index >= len(opponent_staging):
        return False
    target_card = list(opponent_staging[target_index])
    own_staging[own_index] = target_card
    opponent_staging[target_index] = own_card
    add_log(state, tr("single_swap_done", player=display_player(actor_is_p1), own=own_card[0], target=target_card[0]))
    auto_score_same_color_pairs(state, True)
    auto_score_same_color_pairs(state, False)
    clear_tactical_state(state)
    return True


def complete_steal_hand(state, actor_is_p1, target_index):
    opponent_hand = hand_for(state, not actor_is_p1)
    own_hand = hand_for(state, actor_is_p1)
    power_indices = [i for i, card in enumerate(opponent_hand) if card_is_power(card)]
    if target_index >= len(opponent_hand) or target_index not in power_indices:
        return False
    card = opponent_hand.pop(target_index)
    own_hand.append(card)
    add_log(state, tr("steal_done", player=display_player(actor_is_p1), card=card[0]))
    clear_tactical_state(state)
    return True


def complete_destroy(state, actor_is_p1, target_index):
    opponent_hand = hand_for(state, not actor_is_p1)
    if target_index >= len(opponent_hand):
        return False
    card = opponent_hand.pop(target_index)
    add_log(state, tr("destroy_done", player=display_player(actor_is_p1), card=card[0]))
    clear_tactical_state(state)
    return True


# ============================================================
# Session Setup and Lobby
# ============================================================
install_game_audio()

if "room_code" not in st.session_state:
    st.session_state.room_code = None
if "my_player_is_p1" not in st.session_state:
    st.session_state.my_player_is_p1 = None
if "my_profession" not in st.session_state:
    st.session_state.my_profession = None

if st.session_state.room_code is None:
    st.title(T["page_title"])
    st.caption(T["room_caption"])
    room_input = st.text_input(T["room_input_label"])
    player_choice = st.radio(T["you_are"], ["Player 1", "Player 2"], horizontal=True)
    profession_choice = st.selectbox(
        T["profession_label"],
        options=PROFESSION_KEYS,
        format_func=lambda key: f"{display_profession(key)} — {PROFESSION_DESCRIPTIONS[LANG][key]}",
    )
    if st.button(T["join_create"], type="primary"):
        if room_input.strip():
            st.session_state.room_code = room_input.strip()
            st.session_state.my_player_is_p1 = player_choice == "Player 1"
            st.session_state.my_profession = profession_choice
            st.rerun()
        st.warning(T["room_warn"])
    st.stop()

room_code = st.session_state.room_code
my_player_is_p1 = st.session_state.my_player_is_p1
my_player_name = display_player(my_player_is_p1)
state = load_game(room_code)

# ============================================================
# Restart: choose professions again
# ============================================================
if state.get("restart_requested", False):
    st.info(
        "Choose your profession for the new game / "
        "选择新游戏职业 / Pilih profesion untuk permainan baharu"
    )

    my_restart_key = (
        "restart_p1_profession"
        if my_player_is_p1
        else "restart_p2_profession"
    )

    my_restart_profession = state.get(my_restart_key)

    if my_restart_profession is None:
        restart_choice = st.selectbox(
            T["profession_label"],
            options=PROFESSION_KEYS,
            format_func=lambda key: (
                f"{display_profession(key)} — "
                f"{PROFESSION_DESCRIPTIONS[LANG][key]}"
            ),
            key=(
                "restart_p1_choice"
                if my_player_is_p1
                else "restart_p2_choice"
            ),
        )

        if st.button(
            "Confirm Profession / 确认职业 / Sahkan Profesion",
            key=(
                "confirm_restart_p1"
                if my_player_is_p1
                else "confirm_restart_p2"
            ),
        ):
            state[my_restart_key] = restart_choice
            save_game(room_code, state)
            st.rerun()
    else:
        st.success(
            "Your new profession is selected / "
            f"你的新职业：{display_profession(my_restart_profession)}"
        )

    p1_restart_profession = state.get("restart_p1_profession")
    p2_restart_profession = state.get("restart_p2_profession")

    if p1_restart_profession and p2_restart_profession:
        new_state = restart_with_selected_professions(
            p1_restart_profession,
            p2_restart_profession,
        )
        
        components.html(
            """
            <script>
            window.parent.__carbonMatchVictoryPlayed = false;
            </script>
            """,
            height=0,
            width=0,
        )

        save_game(room_code, new_state)
        st.rerun()
    else:
        st.warning(
            "Waiting for both players to choose a profession / "
            "等待双方选择职业 / "
            "Menunggu kedua-dua pemain memilih profesion"
        )

    st.stop()
# Safety check: score any same-color pairs already present in the staging areas.
pairs_changed = False
if auto_score_same_color_pairs(state, True):
    pairs_changed = True
if auto_score_same_color_pairs(state, False):
    pairs_changed = True
if pairs_changed:
    save_game(room_code, state)

if register_profession(state, my_player_is_p1, st.session_state.my_profession):
    save_game(room_code, state)

if resolve_pending_power(state):
    save_game(room_code, state)

if check_game_over_and_settle(state):
    save_game(room_code, state)


# ============================================================
# Original-style Background Music Block
# Keep BGM files directly under assets/. Special audio is under assets/sfx/.
# ============================================================
assets_dir = Path(__file__).parent / "assets"
music_files = sorted(assets_dir.glob("*.mp3"))

if music_files:
    music_names = [music_file.stem for music_file in music_files]
    selected_music_name = st.selectbox(
        "🎵 选择背景音乐",
        music_names,
        key="selected_background_music",
    )
    selected_music = next(
        music_file for music_file in music_files if music_file.stem == selected_music_name
    )
    st.audio(selected_music.read_bytes(), format="audio/mp3")
else:
    st.warning("assets 文件夹中没有找到 MP3 音乐文件。")


# ============================================================
# Header
# ============================================================
my_profession = profession_for(state, my_player_is_p1)
header_profession = display_profession(my_profession or st.session_state.my_profession)
top_left, top_right = st.columns([4, 1])
with top_left:
    st.title(T["page_title"])
    st.caption(
        tr(
            "room_header",
            room=room_code,
            player=my_player_name,
            profession=header_profession,
        )
    )
with top_right:
    if st.button(T["leave_room"]):
        st.session_state.room_code = None
        st.session_state.my_player_is_p1 = None
        st.session_state.my_profession = None
        st.rerun()

can_act = (
    state["turn"] == my_player_name
    and not state["game_over"]
    and state.get("pending_power") is None
)

deck_count = len(state["deck"])
st.markdown(
    f"""
    <div style="background:linear-gradient(135deg,#2c3e50,#4ca1af);padding:14px;border-radius:12px;
                text-align:center;color:white;margin-bottom:20px;box-shadow:0 4px 6px rgba(0,0,0,0.1);">
        <h3 style="margin:0;font-size:22px;">{T['deck_status']}</h3>
        <p style="margin:6px 0 0 0;font-size:26px;font-weight:bold;color:#f1c40f;">{tr('cards_remaining', count=deck_count)}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

top1, top2, top3, top4 = st.columns(4)
top1.metric(T["current_turn"], state["turn"])
current_base_ap = base_ap_for(state, state["turn"] == "Player 1")
top2.metric(T["current_ap"], f"{state['ap']} (base {current_base_ap})")
top3.metric(T["score_label"], f"P1: {state['p1_score']} | P2: {state['p2_score']}")
if top4.button(T["restart"], use_container_width=True):
    state["restart_requested"] = True
    state["restart_p1_profession"] = None
    state["restart_p2_profession"] = None
    save_game(room_code, state)
    st.rerun()

# ============================================================
# Pending Ban Window and Victory Music
# ============================================================
pending = state.get("pending_power")
if pending:
    pending_actor = display_player(pending["actor_is_p1"])
    remaining = max(0, int(pending["deadline"] - time.time() + 0.999))
    if pending["actor_is_p1"] != my_player_is_p1:
        st.warning(tr("ban_window", player=pending_actor, card=pending["card"][0], seconds=remaining))
    else:
        st.info(tr("ban_wait", player=pending_actor))

if state["game_over"]:
    p1_score = state["p1_score"]
    p2_score = state["p2_score"]
    if p1_score > p2_score:
        winner_text, winner_score = "Player 1", p1_score
    elif p2_score > p1_score:
        winner_text, winner_score = "Player 2", p2_score
    else:
        winner_text, winner_score = "Draw", f"P1: {p1_score} / P2: {p2_score}"
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,#f12711,#f5af19);padding:25px;border-radius:15px;
                    text-align:center;color:white;margin-bottom:25px;box-shadow:0 8px 16px rgba(0,0,0,0.3);">
            <h1 style="margin:0;font-size:36px;">🏆 {T['game_settled']} 🏆</h1>
            <p style="margin:15px 0 0 0;font-size:28px;font-weight:bold;">{tr('game_over_msg', winner=winner_text, score=winner_score)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    components.html(
        """
        <script>
        window.parent.__carbonMatchAudio?.playVictoryMusic();
        </script>
        """,
        height=0,
        width=0,
    )

st.markdown("---")


# ============================================================
# Player Column Renderer
# ============================================================
def render_player_column(target_is_p1):
    player_name = display_player(target_is_p1)
    player_display = player_name
    is_mine = target_is_p1 == my_player_is_p1
    turn_is_this_player = state["turn"] == player_name and not state["game_over"]
    profession = profession_for(state, target_is_p1)
    staging = staging_for(state, target_is_p1)
    scoring = scoring_for(state, target_is_p1)
    hand = hand_for(state, target_is_p1)
    score = score_for(state, target_is_p1)
    zone_label = T["p1_zone"] if target_is_p1 else T["p2_zone"]
    if is_mine:
        zone_label += T["you_suffix"]

    with st.container():
        st.markdown(f"### {zone_label}")
        st.caption(
            tr(
                "profession_display",
                profession=display_profession(profession),
            )
        )

        player_debuff_key = (
            "p1_emissions_debuff"
            if target_is_p1
            else "p2_emissions_debuff"
        )

        if state.get(player_debuff_key, False):
            st.warning(T["regulator_debuff_active"])
            
        chaos_free_key = (
            "p1_free_power_remaining"
            if target_is_p1
            else "p2_free_power_remaining"
        )
        chaos_double_key = (
            "p1_double_power_next"
            if target_is_p1
            else "p2_double_power_next"
        )
        chaos_peek_key = (
            "p1_peeked_card"
            if target_is_p1
            else "p2_peeked_card"
        )

        if state.get(chaos_free_key, 0) > 0:
            st.success(T["chaos_status_free"])

        if state.get(chaos_double_key, False):
            st.warning(T["chaos_status_double"])

        if state.get(chaos_peek_key) is not None:
            st.info(T["chaos_status_peek"])

        if turn_is_this_player:
            if is_mine:
                st.success(tr("your_turn", ap=state["ap"]))
            else:
                st.info(T["opp_turn"])
        else:
            st.caption(tr("current_score", score=score))

        # Active player's three normal turn controls.
        if is_mine and can_act:
            b1, b2, b3 = st.columns(3)
            with b1:
                if st.button(T["draw_card"], key=f"draw_{player_name}"):
                    if state["ap"] <= 0 or not state["deck"]:
                        st.warning(T["draw_warn"])
                    else:
                        drawn = state["deck"].pop(0)
                        state["ap"] -= 1
                        if drawn[1] in ["B", "R"]:
                            staging.append(drawn)
                            add_log(state, tr("draw_number", player=player_name, value=drawn[0], color=drawn[1]))
                            auto_score_same_color_pairs(state, target_is_p1)
                        elif drawn[0] == "Chaos Card":
                            add_log(state, tr("draw_chaos", player=player_name))
                            apply_chaos(state, target_is_p1)
                        else:
                            hand.append(drawn)
                            add_log(state, tr("draw_power", player=player_name, card=drawn[0]))
                        check_game_over_and_settle(state)
                        save_game(room_code, state)
                        st.rerun()
            with b2:
                if st.button(T["neutralize"], key=f"neutral_{player_name}"):
                    if len(staging) < 2:
                        st.warning(T["neutral_warn_few"])
                    elif not neutralize_first_mixed_pair(state, target_is_p1):
                        st.warning(T["neutral_warn_no_pair"])
                    else:
                        save_game(room_code, state)
                        st.rerun()
            with b3:
                if st.button(T["end_turn"], key=f"end_{player_name}"):
                    peek_key = "p1_peeked_card" if target_is_p1 else "p2_peeked_card"
                    state[peek_key] = None
                    clear_tactical_state(state)
                    state["turn"] = "Player 2" if target_is_p1 else "Player 1"
                    set_turn_ap(state, not target_is_p1)
                    add_log(state, tr("end_turn_log", player=state["turn"]))
                    save_game(room_code, state)
                    st.rerun()

            if profession == "Emissions Regulator":
                used_key = "p1_emissions_used" if target_is_p1 else "p2_emissions_used"
                if not state[used_key]:
                    if st.button(T["use_profession"], key=f"regulator_{player_name}"):
                        state[used_key] = True
                        debuff_key = "p2_emissions_debuff" if target_is_p1 else "p1_emissions_debuff"
                        state[debuff_key] = True
                        add_log(state, tr("regulator_applied"))
                        save_game(room_code, state)
                        st.rerun()
                    st.caption(T["regulator_ready"])
                else:
                    st.caption(T["profession_used"])

        st.markdown("---")

        # Hand cards.
        st.markdown(tr("hand_title", player=player_display))
        pending_for_defender = state.get("pending_power") and state["pending_power"]["actor_is_p1"] != my_player_is_p1
        if (
            can_act
            and not is_mine
            and target_is_p1 != state.get("tactical_player")
            and state.get("active_tactical") == "Destroy"
        ):
            st.info(T["destroy_hint"])
        elif (
            can_act
            and not is_mine
            and target_is_p1 != state.get("tactical_player")
            and state.get("active_tactical") == "Steal"
        ):
            st.info(T["steal_hint"])

        if hand:
            cols = st.columns(max(1, min(len(hand), 4)))
            for index, card in enumerate(list(hand)):
                with cols[index % len(cols)]:
                    st.markdown(render_card_html(card[0], card[1], size="large"), unsafe_allow_html=True)
                    if is_mine and pending_for_defender and card[0] == "Ban":
                        if st.button(T["ban_btn"], key=f"ban_{player_name}_{index}"):
                            if cancel_pending_power_with_ban(state, my_player_is_p1):
                                save_game(room_code, state)
                                st.rerun()
                    elif is_mine and can_act and card_is_power(card):
                        if card[0] == "Ban":
                            st.caption(T["ban_unavailable"])
                        else:
                            label = f"⚡ {tr('play_btn', number=index + 1)}"
                            if st.button(label, key=f"play_{player_name}_{index}"):
                                ok, error = start_power_card(state, target_is_p1, index)
                                if not ok:
                                    st.warning(error)
                                else:
                                    save_game(room_code, state)
                                    st.rerun()
                    elif can_act and not is_mine and state.get("active_tactical") == "Steal" and target_is_p1 != state.get("tactical_player") and card_is_power(card):
                        if st.button(tr("steal_btn", number=index + 1), key=f"steal_hand_{player_name}_{index}"):
                            if complete_steal_hand(state, my_player_is_p1, index):
                                save_game(room_code, state)
                                st.rerun()
                    elif can_act and not is_mine and state.get("active_tactical") == "Destroy" and target_is_p1 != state.get("tactical_player"):
                        if st.button(tr("destroy_btn", number=index + 1), key=f"destroy_hand_{player_name}_{index}"):
                            if complete_destroy(state, my_player_is_p1, index):
                                save_game(room_code, state)
                                st.rerun()
        else:
            st.caption(T["hand_empty"])

        # Private peek information for the owner only.
        peek_key = "p1_peeked_card" if target_is_p1 else "p2_peeked_card"
        if is_mine and state.get(peek_key):
            peeked = state[peek_key]
            st.info(f"{T['peek_card']}: {peeked[0]} ({peeked[1]}) — {T['peek_note']}")

        st.markdown("---")

        # Staging area and tactical targeting.
        st.markdown(tr("staging_title", player=player_display))
        active = state.get("active_tactical")
        actor = state.get("tactical_player")
        if active == "Push" and can_act and target_is_p1 == actor:
            st.info(T["push_hint"])
        elif active == "Single Swap" and can_act:
            if state.get("q_selected_own_card") is None and target_is_p1 == actor:
                st.info(T["single_swap_hint_own"])
            elif state.get("q_selected_own_card") is not None and target_is_p1 != actor:
                st.info(T["single_swap_hint_opp"])
        elif active == "Steal Staging" and can_act and target_is_p1 != actor:
            st.info(T["steal_staging_hint"])

        if staging:
            cols = st.columns(max(1, min(len(staging), 4)))
            for index, card in enumerate(list(staging)):
                with cols[index % len(cols)]:
                    st.markdown(render_card_html(card[0], card[1], size="medium"), unsafe_allow_html=True)
                    if can_act and active == "Push" and target_is_p1 == actor:
                        if st.button(tr("push_btn", number=index + 1), key=f"push_{player_name}_{index}"):
                            if complete_push(state, my_player_is_p1, index):
                                save_game(room_code, state)
                                st.rerun()
                    elif can_act and active == "Steal Staging" and target_is_p1 != actor:
                        if st.button(tr("steal_btn", number=index + 1), key=f"steal_staging_{player_name}_{index}"):
                            if complete_steal_staging(state, my_player_is_p1, index):
                                save_game(room_code, state)
                                st.rerun()
                    elif can_act and active == "Single Swap":
                        if state.get("q_selected_own_card") is None and target_is_p1 == actor:
                            if st.button(tr("select_btn", number=index + 1), key=f"select_{player_name}_{index}"):
                                if complete_single_swap(state, my_player_is_p1, index):
                                    save_game(room_code, state)
                                    st.rerun()
                        elif state.get("q_selected_own_card") is not None and target_is_p1 != actor:
                            if st.button(tr("swap_btn", number=index + 1), key=f"swap_{player_name}_{index}"):
                                if complete_single_swap(state, my_player_is_p1, index):
                                    save_game(room_code, state)
                                    st.rerun()
        else:
            st.caption(T["staging_empty"])

        st.markdown("---")

        # Scoring area.
        st.markdown(tr("scored_title", player=player_display, score=score))
        if scoring:
            for pair_index, pair in enumerate(scoring):
                st.markdown(tr("pair_label", number=pair_index + 1))
                pair_cols = st.columns(2)
                with pair_cols[0]:
                    st.markdown(render_card_html(pair[0][0], pair[0][1], size="small"), unsafe_allow_html=True)
                with pair_cols[1]:
                    st.markdown(render_card_html(pair[1][0], pair[1][1], size="small"), unsafe_allow_html=True)
        else:
            st.caption(T["scored_empty"])


# ============================================================
# Main Layout
# ============================================================
st_autorefresh(interval=2000, key="carbon_match_v2_refresh")
col_p1, col_p2 = st.columns(2)
with col_p1:
    render_player_column(True)
with col_p2:
    render_player_column(False)

st.markdown("---")
st.subheader("📋 Game Dynamic Logs")
log_container = st.container(height=220)
with log_container:
    for log_entry in state["logs"]:
        st.markdown(f"- {html.escape(str(log_entry))}")
