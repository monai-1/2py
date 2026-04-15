import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
from io import BytesIO

# -------------------------- 页面全局配置 --------------------------
st.set_page_config(
    page_title="人格天道",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -------------------------- 核心CSS：国风样式+元素专属动画 --------------------------
st.markdown("""
<style>
/* 全局国风基础样式 */
.main {background-color: #F8F5F0;}
.stRadio>label {font-size: 16px; color: #2C2C2C; font-weight: bold;}
.stButton>button {
    background: linear-gradient(90deg, #8B4513, #A0522D);
    color: white;
    border-radius: 8px;
    padding: 8px 24px;
    font-size: 16px;
    border: none;
    box-shadow: 0 2px 8px rgba(139, 69, 19, 0.3);
    transition: all 0.3s ease;
}
.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(139, 69, 19, 0.5);
}
.title {text-align: center; color: #8B4513; font-family: "SimHei";}
.subtitle {text-align: center; color: #696969;}
.result-box {
    border: 2px solid #8B4513;
    border-radius: 12px;
    padding: 24px;
    background-color: #FFFDF8;
    box-shadow: 0 4px 16px rgba(139, 69, 19, 0.2);
}

/* 通用淡入动画 */
@keyframes fadeIn {
    from {opacity: 0; transform: translateY(20px);}
    to {opacity: 1; transform: translateY(0);}
}
.fade-in {animation: fadeIn 0.8s ease forwards;}
.delay-1 {animation-delay: 0.2s;}
.delay-2 {animation-delay: 0.4s;}
.delay-3 {animation-delay: 0.6s;}
.delay-4 {animation-delay: 0.8s;}

/* 元素专属标题动画 */
/* 火元素动画：火焰闪烁 */
@keyframes fireGlow {
    0%,100% {text-shadow: 0 0 8px #FF4500, 0 0 16px #FF2500; color: #FF4500;}
    50% {text-shadow: 0 0 16px #FF4500, 0 0 32px #FF6500; color: #FF6500;}
}
.fire-title {animation: fireGlow 2s ease-in-out infinite; font-family: "SimHei"; text-align: center;}

/* 水元素动画：水波纹流动 */
@keyframes waterFlow {
    0%,100% {text-shadow: 0 0 8px #1E90FF, 0 0 16px #00BFFF; color: #1E90FF;}
    50% {text-shadow: 0 0 16px #1E90FF, 0 0 32px #87CEFA; color: #00BFFF;}
}
.water-title {animation: waterFlow 2s ease-in-out infinite; font-family: "SimHei"; text-align: center;}

/* 土元素动画：厚重沉稳微光 */
@keyframes earthGlow {
    0%,100% {text-shadow: 0 0 6px #8B4513, 0 0 12px #A0522D; color: #8B4513;}
    50% {text-shadow: 0 0 12px #8B4513, 0 0 24px #CD853F; color: #A0522D;}
}
.earth-title {animation: earthGlow 3s ease-in-out infinite; font-family: "SimHei"; text-align: center;}

/* 风元素动画：飘逸流动 */
@keyframes windFlow {
    0% {text-shadow: 0 0 8px #98FB98, 0 0 16px #90EE90; transform: translateX(0); color: #228B22;}
    50% {text-shadow: 0 0 16px #98FB98, 0 0 32px #90EE90; transform: translateX(5px); color: #32CD32;}
    100% {text-shadow: 0 0 8px #98FB98, 0 0 16px #90EE90; transform: translateX(0); color: #228B22;}
}
.wind-title {animation: windFlow 3s ease-in-out infinite; font-family: "SimHei"; text-align: center;}

/* 雷元素动画：雷霆闪烁 */
@keyframes thunderFlash {
    0%,90%,100% {text-shadow: 0 0 8px #FFD700, 0 0 16px #FFA500; color: #FFD700;}
    92% {text-shadow: 0 0 32px #FFFFFF, 0 0 64px #FFD700; color: #FFFFFF;}
    95% {text-shadow: 0 0 8px #FFD700, 0 0 16px #FFA500; color: #FFD700;}
    97% {text-shadow: 0 0 32px #FFFFFF, 0 0 64px #FFD700; color: #FFFFFF;}
}
.thunder-title {animation: thunderFlash 2s ease-in-out infinite; font-family: "SimHei"; text-align: center;}

/* 双元素/万象通用动画 */
.dual-title {
    background: linear-gradient(90deg, #8B4513, #696969, #8B4513);
    -webkit-background-clip: text;
    color: transparent;
    animation: gradientShift 3s ease infinite;
    font-family: "SimHei";
    text-align: center;
}
@keyframes gradientShift {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* 评语文字特效 */
.comment-text {
    line-height: 1.8;
    font-size: 15px;
    color: #2C2C2C;
    font-family: "SimSun";
    animation: fadeIn 1.2s ease forwards;
    animation-delay: 1s;
    opacity: 0;
}
</style>
""", unsafe_allow_html=True)

# -------------------------- 全局初始化 --------------------------
# 分数持久化
if "scores" not in st.session_state:
    st.session_state.scores = {
        "火": 0,
        "水": 0,
        "土": 0,
        "风": 0,
        "雷": 0
    }
# 答题完成状态
if "test_finished" not in st.session_state:
    st.session_state.test_finished = False

# 元素固定顺序（用于优先级判断）
element_order = ["火", "水", "土", "风", "雷"]

# 16人格稳定图片直链
img_urls = {
    "阳炎": "https://ugc-img.ifengimg.com/img/2021-11-27%20101337/dialog_020177556274.jpg",
    "净水": "https://xxjs.yiban.cn/filesystem/ns1/0f/a9/4d/53/475ff357e8f2aa86.jpeg",
    "玄土": "https://ts3.tc.mm.bing.net/th/id/OIP-C.mN_arwUOoQPBqx38_2Ur6wHaEK?rs=1&pid=ImgDetMain&o=7&rm=3",
    "罡风": "https://bpic.588ku.com/video_library/cover/24/04/09/5530d1e0e2e5cacba62ec56a268606df_snapshot_t0.jpg",
    "绛雷": "https://ts4.tc.mm.bing.net/th/id/OIP-C.SpX8Vb1ZlvUWwX2qn-EyhwHaE7?rs=1&pid=ImgDetMain&o=7&rm=3",
    "烈岩": "https://ts1.tc.mm.bing.net/th/id/OIP-C.9-xt6xP-XbGSPDb5FGETQwHaEJ?rs=1&pid=ImgDetMain&o=7&rm=3",
    "沼泽": "https://p1.ssl.qhmsg.com/t011aee2ea4ab5a462a.jpg",
    "离飓": "https://ts1.tc.mm.bing.net/th/id/R-C.b3d44317e30d0d13f3bbbf0e4be6afe8?rik=SB8vqbM%2faC6neg&riu=http%3a%2f%2fimg.sucaijishi.com%2fuploadfile%2f2023%2f0117%2f20230117045456693.png%3fimageMogr2%2fformat%2fjpg%2fblur%2f1x0%2fquality%2f60&ehk=EyAxXXj9AxI8HbEak35yQOsmqSD2IFofl91G67PYbbE%3d&risl=&pid=ImgRaw&r=0",
    "冥幽": "https://ts2.tc.mm.bing.net/th/id/OIP-C.-8Mh1BflkSzHpOJqKp-a1wHaDJ?rs=1&pid=ImgDetMain&o=7&rm=3",
    "尘界": "https://n.sinaimg.cn/sinacn15/50/w1000h650/20180807/dea3-hhkuskt1061210.jpg",
    "焚霆": "https://ts2.tc.mm.bing.net/th/id/OIP-C.gtLDPofebgcx_bDkvCy0uAHaFk?rs=1&pid=ImgDetMain&o=7&rm=3",
    "坎狱": "https://pic4.zhimg.com/v2-88feb070495e800c29acf28149c86bf4_r.jpg?source=1940ef5c",
    "天暴": "https://ts4.tc.mm.bing.net/th/id/OIP-C.bu4l0pBibjQ3zaeC4VzbxgHaEK?rs=1&pid=ImgDetMain&o=7&rm=3",
    "磁宫": "https://ts3.tc.mm.bing.net/th/id/OIP-C.b6ZYFlQ_V9Ys5p0ti1fwIwHaHa?rs=1&pid=ImgDetMain&o=7&rm=3",
    "两仪": "https://preview.qiantucdn.com/agency/dt/xsj/1t/yc/z7.jpg!w1024_new_small_1",
    "万象": "https://ts1.tc.mm.bing.net/th/id/R-C.74018933c94e7fa0c4d52568aadbbd53?rik=a7eZ%2b8O0A7hn1w&riu=http%3a%2f%2fwww.uux.cn%2fattachments%2f2010%2f05%2f1_201005171431191NC0k.jpg&ehk=HPcMFuqOz8lK4%2bkWzJ%2bhUPj1DDQzoxPaU5Zc8UNdHSg%3d&risl=&pid=ImgRaw&r=0"
}

# 16人格完整道学评语
personality_comments = {
    "阳炎": "【阳炎人格】五行属火，秉离卦之精，心性通明，热情似骄阳。行事雷厉风行，有破釜沉舟之勇；待人赤诚热烈，具暖化万物之能。然火性过刚，易躁易折，需以静制动，以柔济刚，方合水火既济之道。《道德经》云：“躁胜寒，静胜热，清静为天下正。”若能守心如一，不骄不躁，则天命所归，前程似锦。",
    "净水": "【净水人格】五行属水，承坎卦之德，心性温润，包容如江海。行事沉稳从容，有润物无声之善；待人谦和有礼，具海纳百川之量。水性至柔，却能克刚，需以韧为基，以动为辅，方合流水不腐之理。《道德经》云：“上善若水，水善利万物而不争。”若能坚守本心，不随波逐流，则福泽深厚，万事顺遂。",
    "玄土": "【玄土人格】五行属土，载坤卦之厚，心性稳重，坚韧如大地。行事踏实可靠，有厚德载物之责；待人忠厚诚恳，具包容万物之量。土性主静，却能生金，需以变为辅，以通为要，方合土生万物之理。《周易》云：“地势坤，君子以厚德载物。”若能守正出奇，不固步自封，则基业稳固，大有可为。",
    "罡风": "【罡风人格】五行属风，携巽卦之灵，心性灵动，自由如清风。行事灵活变通，有顺势而为之智；待人洒脱不羁，具逍遥自在之态。风性无定，却能化雨，需以定为基，以恒为要，方合风行天下之理。《道德经》云：“飘风不终朝，骤雨不终日。”若能收放自如，不飘忽不定，则心境通达，万事亨通。",
    "绛雷": "【绛雷人格】五行属雷，振震卦之威，心性果敢，锐利如雷霆。行事刚正不阿，有雷霆破局之勇；待人直言不讳，具明辨是非之能。雷性刚烈，却能生春，需以柔济刚，以和为贵，方合雷动万物之理。《周易》云：“震来虩虩，笑言哑哑。”若能威而不猛，不疾言厉色，则声威远扬，功成名就。",
    "烈岩": "【烈岩人格】五行属火土，秉离坤相合之象，心性热烈而稳重，如火燃大地。行事热情主动，却能踏实可靠；待人赤诚忠厚，却能坚守原则。火土相生，却能相制，需以稳为基，以热为辅，方合火土相生之理。《周易》云：“离上坤下，明夷。君子以莅众，用晦而明。”若能明辨是非，不骄不躁，则事业有成，前程似锦。",
    "沼泽": "【沼泽人格】五行属水土，承坎坤相合之象，心性温润而稳重，如水润大地。行事沉稳从容，却能灵活变通；待人谦和有礼，却能坚守底线。水土相生，却能相制，需以柔为基，以稳为辅，方合水土相生之理。《道德经》云：“上善若水，水善利万物而不争。”若能坚守本心，不随波逐流，则福泽深厚，万事顺遂。",
    "离飓": "【离飓人格】五行属火风，携离巽相合之象，心性热烈而灵动，如火借风势。行事热情主动，却能灵活变通；待人赤诚热烈，却能洒脱不羁。火风相生，却能相制，需以热为基，以灵为辅，方合火风相生之理。《道德经》云：“飘风不终朝，骤雨不终日。”若能收放自如，不飘忽不定，则心境通达，万事亨通。",
    "冥幽": "【冥幽人格】五行属水风，承坎巽相合之象，心性温润而灵动，如水随风行。行事沉稳从容，却能灵活变通；待人谦和有礼，却能洒脱不羁。水风相生，却能相制，需以柔为基，以灵为辅，方合水风相生之理。《道德经》云：“上善若水，水善利万物而不争。”若能坚守本心，不随波逐流，则福泽深厚，万事顺遂。",
    "尘界": "【尘界人格】五行属土风，载坤巽相合之象，心性稳重而灵动，如大地随风。行事踏实可靠，却能灵活变通；待人忠厚诚恳，却能洒脱不羁。土风相生，却能相制，需以稳为基，以灵为辅，方合土风相生之理。《周易》云：“地势坤，君子以厚德载物。”若能守正出奇，不固步自封，则基业稳固，大有可为。",
    "焚霆": "【焚霆人格】五行属火雷，振离震相合之象，心性热烈而果敢，如火伴雷霆。行事热情主动，却能刚正不阿；待人赤诚热烈，却能直言不讳。火雷相生，却能相制，需以热为基，以刚为辅，方合火雷相生之理。《周易》云：“震来虩虩，笑言哑哑。”若能威而不猛，不疾言厉色，则声威远扬，功成名就。",
    "坎狱": "【坎狱人格】五行属水雷，承坎震相合之象，心性温润而果敢，如水伴雷霆。行事沉稳从容，却能刚正不阿；待人谦和有礼，却能直言不讳。水雷相生，却能相制，需以柔为基，以刚为辅，方合水雷相生之理。《道德经》云：“上善若水，水善利万物而不争。”若能坚守本心，不随波逐流，则福泽深厚，万事顺遂。",
    "天暴": "【天暴人格】五行属风雷，携巽震相合之象，心性灵动而果敢，如风伴雷霆。行事灵活变通，却能刚正不阿；待人洒脱不羁，却能直言不讳。风雷相生，却能相制，需以灵为基，以刚为辅，方合风雷相生之理。《道德经》云：“飘风不终朝，骤雨不终日。”若能收放自如，不飘忽不定，则心境通达，万事亨通。",
    "磁宫": "【磁宫人格】五行属土雷，载坤震相合之象，心性稳重而果敢，如大地伴雷霆。行事踏实可靠，却能刚正不阿；待人忠厚诚恳，却能直言不讳。土雷相生，却能相制，需以稳为基，以刚为辅，方合土雷相生之理。《周易》云：“地势坤，君子以厚德载物。”若能守正出奇，不固步自封，则基业稳固，大有可为。",
    "两仪": "【两仪人格】五行属水火，承坎离既济之象，心性平衡，阴阳调和。行事刚柔并济，有中庸之道；待人不偏不倚，具包容之量。水火本相克，却能相济，需以守中为要，以调和为基，方合阴阳平衡之理。《道德经》云：“万物负阴而抱阳，冲气以为和。”若能守心如一，不偏不倚，则福慧双修，前程似锦。",
    "万象": "【万象人格】五行均衡，承太极万象之象，心性包容，道化自然。行事随遇而安，有包容万物之量；待人和气致祥，具化育万物之能。五灵均衡，却能生万象，需以自然为要，以无为为基，方合道化自然之理。《道德经》云：“人法地，地法天，天法道，道法自然。”若能顺应自然，不刻意强求，则万事顺遂，福泽深厚。"
}

# 人格对应元素动画映射
title_animation_map = {
    "阳炎": "fire-title",
    "净水": "water-title",
    "玄土": "earth-title",
    "罡风": "wind-title",
    "绛雷": "thunder-title",
    "烈岩": "fire-title",
    "沼泽": "water-title",
    "离飓": "fire-title",
    "冥幽": "water-title",
    "尘界": "earth-title",
    "焚霆": "thunder-title",
    "坎狱": "thunder-title",
    "天暴": "wind-title",
    "磁宫": "earth-title",
    "两仪": "dual-title",
    "万象": "dual-title"
}

# -------------------------- 10道测试题（5大方向） --------------------------
questions = [
    # 社交方向
    {"题目": "聚会中你更倾向于？", "选项": ["主动带动气氛", "安静倾听他人", "随和配合大家", "观察全场氛围", "直言表达观点"], "元素": ["火", "水", "土", "风", "雷"]},
    {"题目": "朋友求助时你会？", "选项": ["立刻出手相助", "冷静分析方案", "踏实负责到底", "灵活变通处理", "果断给出建议"], "元素": ["火", "水", "土", "风", "雷"]},
    # 家庭方向
    {"题目": "面对家庭安排你会？", "选项": ["热情参与其中", "温和协调关系", "稳重遵从传统", "随性自在相处", "直接表达想法"], "元素": ["火", "水", "土", "风", "雷"]},
    {"题目": "家庭矛盾时你会？", "选项": ["主动化解冲突", "冷静安抚情绪", "坚守原则底线", "顺势缓和气氛", "公正指出问题"], "元素": ["火", "水", "土", "风", "雷"]},
    # 心理方向
    {"题目": "遇到压力你会？", "选项": ["积极迎难而上", "静心调整心态", "沉稳默默扛住", "洒脱放下执念", "勇敢突破困境"], "元素": ["火", "水", "土", "风", "雷"]},
    {"题目": "自我评价更像？", "选项": ["热烈外向", "温柔内敛", "坚韧踏实", "自由灵动", "果敢锐利"], "元素": ["火", "水", "土", "风", "雷"]},
    # 政治方向
    {"题目": "看待规则你认为？", "选项": ["热情推动革新", "温和维护平衡", "稳重坚守秩序", "灵活适应变化", "公正坚守底线"], "元素": ["火", "水", "土", "风", "雷"]},
    {"题目": "面对争议你会？", "选项": ["主动发声表态", "冷静客观分析", "务实寻求共识", "随缘不执对错", "果断明辨是非"], "元素": ["火", "水", "土", "风", "雷"]},
    # 宇宙观方向
    {"题目": "你相信人生是？", "选项": ["热烈绽放的旅程", "温润包容的修行", "厚重踏实的积累", "自由无拘的漂泊", "雷霆破局的蜕变"], "元素": ["火", "水", "土", "风", "雷"]},
    {"题目": "面对未知你会？", "选项": ["勇敢探索", "静心感悟", "踏实求证", "随性接纳", "果断揭秘"], "元素": ["火", "水", "土", "风", "雷"]}
]

# -------------------------- 页面标题 --------------------------
st.markdown("<h1 class='title'>人格天道</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>道生万物，五灵显形，测你本命人格</p>", unsafe_allow_html=True)
st.divider()

# -------------------------- 分区1：问题区（取消初始选择） --------------------------
st.markdown("## 🌌 问题区")
st.markdown("请根据内心真实想法选择，共10道题，**所有题目均为必填**")

# 存储用户答案，默认无选择
answers = []
for i, q in enumerate(questions):
    ans = st.radio(
        f"第{i+1}题：{q['题目']}",
        q["选项"],
        key=f"q{i}",
        index=None,  # 核心优化：取消初始默认选择
        horizontal=False
    )
    answers.append(ans)

# -------------------------- 分区2：加分区 --------------------------
st.markdown("## 📊 加分区")
submit_btn = st.button("✅ 提交所有答案，计算本命人格")

if submit_btn:
    # 校验：所有题目必须完成选择
    if None in answers:
        st.error("⚠️ 你还有题目未完成选择，请答完所有题目后再提交！")
        st.session_state.test_finished = False
    else:
        # 重置分数
        for key in st.session_state.scores:
            st.session_state.scores[key] = 0
        
        # 按选择对应元素加分
        for i, ans in enumerate(answers):
            idx = questions[i]["选项"].index(ans)
            elem = questions[i]["元素"][idx]
            st.session_state.scores[elem] += 10
        
        # 标记答题完成
        st.session_state.test_finished = True

# 答题完成后显示分数
if st.session_state.test_finished:
    score_df = pd.DataFrame({
        "元素": list(st.session_state.scores.keys()),
        "分数": list(st.session_state.scores.values())
    })
    st.dataframe(score_df, use_container_width=True, hide_index=True)

# -------------------------- 分区3：判断区（严格按规则 + 新增所有人格总览） --------------------------
st.markdown("## 🔮 判断区")

def get_personality(scores):
    """16种人格判断逻辑（严格遵循需求）"""
    # 1. 筛选≥30分的元素，按「火→水→土→风→雷」固定优先级排序
    qualified_elems = [elem for elem in element_order if scores[elem] >= 30]
    
    # 2. 双元素判断：≥2个元素达标，取前2个（3个及以上也取前2）
    if len(qualified_elems) >= 2:
        elem1, elem2 = qualified_elems[0], qualified_elems[1]
        dual_personality_map = {
            ("火", "水"): "两仪", ("火", "土"): "烈岩", ("火", "风"): "离飓", ("火", "雷"): "焚霆",
            ("水", "火"): "两仪", ("水", "土"): "沼泽", ("水", "风"): "冥幽", ("水", "雷"): "坎狱",
            ("土", "火"): "烈岩", ("土", "水"): "沼泽", ("土", "风"): "尘界", ("土", "雷"): "磁宫",
            ("风", "火"): "离飓", ("风", "水"): "冥幽", ("风", "土"): "尘界", ("风", "雷"): "天暴",
            ("雷", "火"): "焚霆", ("雷", "水"): "坎狱", ("雷", "土"): "磁宫", ("雷", "风"): "天暴"
        }
        return dual_personality_map[(elem1, elem2)], f"{elem1}{elem2}"
    
    # 3. 单元素判断：仅1个元素达标
    elif len(qualified_elems) == 1:
        single_map = {"火": "阳炎", "水": "净水", "土": "玄土", "风": "罡风", "雷": "绛雷"}
        return single_map[qualified_elems[0]], qualified_elems[0]
    
    # 4. 无元素达标：取最高分，多元素同分则为万象
    else:
        max_score = max(scores.values())
        top_elems = [elem for elem in element_order if scores[elem] == max_score]
        if len(top_elems) >= 2:
            return "万象", "均衡"
        else:
            single_map = {"火": "阳炎", "水": "净水", "土": "玄土", "风": "罡风", "雷": "绛雷"}
            return single_map[top_elems[0]], top_elems[0]

# 原有功能：显示人格判断结果
if st.session_state.test_finished:
    personality, main_elem = get_personality(st.session_state.scores)
    st.success(f"**你的本命人格：{personality}** | 核心属性：{main_elem}")
else:
    st.info("请完成所有题目并提交，将自动为你测算本命人格")

# ====================== 新增功能：所有人格及概念图 ======================
st.markdown("---")
st.markdown("### 📚 所有人格总览 & 概念图")
show_all = st.button("📖 展开/收起 16种人格全集")

# 用session_state控制展开/收起
if "show_all_personality" not in st.session_state:
    st.session_state.show_all_personality = False

if show_all:
    st.session_state.show_all_personality = not st.session_state.show_all_personality

# 展开时显示所有人格
if st.session_state.show_all_personality:
    all_personas = list(img_urls.keys())
    # 分4列展示，美观整齐
    cols = st.columns(4)
    for idx, p in enumerate(all_personas):
        with cols[idx % 4]:
            try:
                res = requests.get(img_urls[p], timeout=5)
                st.image(BytesIO(res.content), caption=p, use_container_width=True)
            except:
                st.image("https://via.placeholder.com/300x200?text="+p, caption=p, use_container_width=True)
            st.caption(personality_comments[p][:50] + "…")

# -------------------------------------------------------------------

# -------------------------- 分区4：输出区（动画+特效优化） --------------------------
st.markdown("## 🏮 输出区")
if st.session_state.test_finished:
    personality, main_elem = get_personality(st.session_state.scores)
    animation_class = title_animation_map[personality]
    
    with st.container():
        st.markdown(f"<div class='result-box'>", unsafe_allow_html=True)
        
        # 1. 人格标题（元素专属动画，延迟0.2s入场）
        st.markdown(f"<h2 class='{animation_class} fade-in delay-1'>【 {personality} 】本命人格</h2>", unsafe_allow_html=True)
        st.divider()
        
        # 2. 本命画像（延迟0.4s入场）
        st.markdown("<div class='fade-in delay-2'>", unsafe_allow_html=True)
        st.markdown("### 🎨 本命画像")
        try:
            response = requests.get(img_urls[personality], timeout=8)
            img = BytesIO(response.content)
            st.image(img, caption=f"{personality} 道学玄幻本命画像", use_container_width=True)
        except:
            st.image("https://via.placeholder.com/800x400?text=五灵人格本命画像", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 3. 五灵分布图表（延迟0.6s入场）
        st.markdown("<div class='fade-in delay-3'>", unsafe_allow_html=True)
        st.markdown("### 📊 五灵元素分布")
        # 优化版图表：带X/Y轴标签，中文完美显示
        plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "WenQuanYi Micro Hei", "Arial Unicode MS"]  # 全局中文设置
        plt.rcParams["axes.unicode_minus"] = False
        fig, ax = plt.subplots(figsize=(7, 4))
        bars = ax.bar(
            st.session_state.scores.keys(),
            st.session_state.scores.values(),
            color=["#FF4500", "#1E90FF", "#8B4513", "#32CD32", "#FFD700"]
        )
        # 图表标签优化
        ax.set_title("五灵元素分数分布", fontsize=14, fontweight="bold")
        ax.set_xlabel("五灵元素", fontsize=12)
        ax.set_ylabel("得分", fontsize=12)
        ax.set_ylim(0, 100)  # 固定Y轴范围，更直观
        plt.xticks(fontsize=11)
        plt.yticks(fontsize=11)
        # 柱状图顶部显示分数
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2.,
                height + 2,
                f"{int(height)}分",
                ha="center",
                va="bottom",
                fontsize=10
            )
        st.pyplot(fig)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 4. 道学评语（文字特效，延迟0.8s入场）
        st.markdown("### 📜 道学本命评语")
        st.markdown(f"<p class='comment-text'>{personality_comments[personality]}</p>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.warning("完成答题并提交后，将自动生成你的专属人格画像、元素分布与道学评语")
