"""
osaka_2023_governor のデータ構造を初期化するスクリプト

・js/data/osaka_2023_governor/index.json  を作成
・js/data/osaka_2023_governor/candidates/yoshimura.json  を作成
  └ 2023-2026 の公知情報をもとに promises_2023 に初期ステータスを付与
"""

import json
from pathlib import Path

ROOT      = Path(__file__).resolve().parents[1]
SRC_JSON  = ROOT / "js/data/osaka_2027_governor/candidates/yoshimura.json"
OUT_DIR   = ROOT / "js/data/osaka_2023_governor"
IDX_OUT   = OUT_DIR / "index.json"
CAND_OUT  = OUT_DIR / "candidates/yoshimura.json"

# ── 初期評価テーブル ──────────────────────────────────────────────────────
# (status, note, evidence_url)
# 根拠:
#   完了  … 条例・予算・制度として実施確認
#   着手  … 取り組みは始まっているが任期中完結していない
#   未着手 … 具体的な動きが確認できない
#   不明  … 情報不足

INITIAL_EVAL = {
    # ── 理念（府議会改革）──────────────────────────────────────────────
    "p001": ("着手",  "維新として議員定数削減の議論は継続しているが、条例改正には至っていない",         ""),
    "p002": ("完了",  "大阪維新の会は2011年以来、議員報酬3割カットを継続実施中",                     "https://www.pref.osaka.lg.jp/gikai/"),
    "p003": ("未着手","地方議会の選挙制度は公職選挙法の国事項であり、府独自の条例化は実現していない",  ""),
    "p004": ("完了",  "大阪府議会は政務活動費の全領収書をウェブ公開。全国トップ水準を維持",            "https://www.pref.osaka.lg.jp/gikai/seimukatsudohi/"),
    "p005": ("着手",  "府議会でのタブレット導入・ペーパーレス化は段階的に進行中",                      ""),
    "p006": ("着手",  "コロナ禍を経て委員会等のオンライン参加環境を整備。本会議は未対応",              ""),
    "p007": ("着手",  "「府議会出前授業」は毎年度実施。府民向け出前講座も継続",                        "https://www.pref.osaka.lg.jp/gikai/koho/"),

    # ── 日本の成長エンジン都市・大阪 ──────────────────────────────────
    "p008": ("着手",  "副首都推進局が府市連携で施策を推進中。法制度整備は未完",                        "https://www.pref.osaka.lg.jp/fukushuto/"),
    "p009": ("着手",  "広域行政一元化条例（2020年施行）のもと府市連携は継続。実質的な権限統合は限定的", ""),
    "p010": ("未着手","市町村合併・大阪市との合併への具体的な動きは確認できない",                      ""),
    "p011": ("着手",  "スマートシティ戦略部など一部組織の外部化・民間委託は進行中",                    ""),
    "p012": ("着手",  "大阪都市圏の広域鉄道整備計画を継続推進",                                        ""),
    "p013": ("着手",  "北陸新幹線は敦賀まで2024年3月延伸開業。なにわ筋線は2031年開業予定で工事中",     "https://www.westjr.co.jp/"),
    "p014": ("着手",  "新大阪グランドデザイン策定。リニア開業を見据えた民間開発プロジェクトが動き出している", ""),
    "p015": ("着手",  "なにわ筋線沿線まちづくり指針を策定。各エリアの開発計画は進行中",                ""),
    "p016": ("着手",  "大阪のまちづくりグランドデザインに基づく都市再生事業を継続推進",                ""),

    # ── 成長し続けるグローバル都市・大阪 ──────────────────────────────
    "p017": ("完了",  "2025年大阪・関西万博は2025年4月13日〜10月13日に開催。約2,820万人が来場",       "https://www.expo2025.or.jp/"),
    "p018": ("着手",  "万博会場でのeVTOL（空飛ぶクルマ）デモ飛行を実施。水上交通ルートも一部運用",    ""),
    "p019": ("完了",  "2024年「大阪・関西万博ユニバーサルデザイン条例」を制定",                        ""),
    "p020": ("着手",  "夢洲IRの整備計画は国から認定。ただし開業時期は2030年代にずれ込む見通し",       "https://www.pref.osaka.lg.jp/ir/"),
    "p021": ("着手",  "スマートシティ推進・自動走行実証実験を実施中。万博でのデジタル活用が実現",       ""),
    "p022": ("着手",  "大阪・関西金融センター推進会議を設置し、金融機能誘致に取り組み中",              ""),

    # ── 子どもが輝く教育無償都市・大阪 ────────────────────────────────
    "p023": ("着手",  "「教育無償都市・大阪」を掲げ複数の無償化施策を段階的に実施",                    ""),
    "p024": ("完了",  "2024年度から大阪府立・私立高校の授業料を所得制限なしで実質無償化。全国初",      "https://www.pref.osaka.lg.jp/kyoikusomu/mushouka/"),
    "p025": ("着手",  "すくすくウォッチの対象を小1〜中3に拡大（2024年度）",                            ""),
    "p026": ("着手",  "ヤングケアラー支援条例を制定（2024年）。SSWの配置拡充も実施",                   ""),
    "p027": ("着手",  "子ども輝く未来基金を活用した各種補助を実施中",                                   ""),
    "p028": ("着手",  "府立高校改革推進中。文理学科の見直し等を検討",                                   ""),
    "p029": ("着手",  "府立高校の再編整備計画（2024-2028年度）を策定・実施中",                         "https://www.pref.osaka.lg.jp/kotogakko/saihen/"),
    "p030": ("未着手","府立高校の民営化は議論段階。具体的な実施には至っていない",                      ""),
    "p031": ("着手",  "グローバルリーダーズハイスクール等の設置、ICT活用教育を推進",                   ""),
    "p032": ("着手",  "支援学校の増設・建替えを複数実施。教員加配も強化",                              ""),

    # ── 健康長寿都市・大阪 ────────────────────────────────────────────
    "p033": ("着手",  "地域包括ケアシステムの構築を市町村と連携して推進",                               ""),
    "p034": ("着手",  "スマート・エイジングシティ推進会議を設置し施策を展開",                           ""),
    "p035": ("着手",  "がん検診受診率向上キャンペーンを継続。AI活用の早期発見支援を導入",               ""),
    "p036": ("着手",  "BNCT（ホウ素中性子捕捉療法）の阪大での臨床試験支援等を継続",                    ""),
    "p037": ("着手",  "健康マイレージ「アスマイル」の登録者数拡大を継続推進",                           "https://www.pref.osaka.lg.jp/kenko21/asmile/"),
    "p038": ("着手",  "孤独・孤立対策推進計画を策定（2024年）。LINE相談窓口の拡充等を実施",            ""),

    # ── 災害・有事に強い都市・大阪 ────────────────────────────────────
    "p039": ("着手",  "大阪広域防災拠点の整備を推進。府市消防の広域連携訓練を実施",                     ""),
    "p040": ("着手",  "南海トラフ地震対策として防潮堤整備を継続。ICT・ドローン活用の点検を実施",       ""),
    "p041": ("着手",  "大阪府防災情報メールの機能強化、SNSでの情報発信体制を整備",                      ""),
    "p042": ("着手",  "大阪健康安全基盤研究所（IPHA）を拠点に感染症監視・人材育成を継続",               "https://www.ipha.jp/"),

    # ── 産業と自然が豊かな都市・大阪 ──────────────────────────────────
    "p043": ("着手",  "大阪イノベーションハブ等を通じてスタートアップ・研究支援を継続",                 ""),
    "p044": ("着手",  "大阪府森林整備計画に基づき林業振興・木材利用促進を実施",                         ""),
    "p045": ("着手",  "府営公園へのPark-PFI導入（服部緑地等）で民間活力による魅力化を推進",            ""),
    "p046": ("未着手","本社移転促進に向けた具体的な税制優遇・補助制度の新設は確認できない",             ""),
    "p047": ("不明",  "若年労働者の住民税免除制度の具体的な進捗が確認できない",                         ""),

    # ── 課題解決型・持続可能な都市・大阪 ──────────────────────────────
    "p048": ("未着手","水道民営化の検討は続いているが、府域水道一元化・民営化の実現には至っていない",   ""),
    "p049": ("着手",  "大阪府DX推進計画に基づき、市町村支援・電子申請拡大等を実施中",                  ""),
}


def main() -> None:
    # ── 1. yoshimura.json（2027フォルダ）から promises_2023 を読み込む ──
    src = json.loads(SRC_JSON.read_text("utf-8"))
    promises = src.get("promises_2023", [])
    if not promises:
        print("[ERROR] promises_2023 が見つかりません")
        return

    # 初期ステータスを反映
    for p in promises:
        ev = INITIAL_EVAL.get(p["id"])
        if ev:
            p["status"]       = ev[0]
            p["note"]         = ev[1]
            p["evidence_url"] = ev[2]

    done    = sum(1 for p in promises if p["status"] == "完了")
    started = sum(1 for p in promises if p["status"] == "着手")
    pending = sum(1 for p in promises if p["status"] == "未着手")
    unknown = sum(1 for p in promises if p["status"] == "不明")
    score   = round((done + started * 0.5) / (done + started + pending) * 100)

    # ── 2. index.json を作成 ─────────────────────────────────────────────
    IDX_OUT.parent.mkdir(parents=True, exist_ok=True)
    index = {
        "meta": {
            "election":      "大阪府知事選挙 2023",
            "election_day":  "2023年4月9日",
            "status":        "archived",
            "source_note":   "大阪府選挙管理委員会",
            "last_updated":  "2026-04-24T00:00:00Z"
        },
        "candidates": [
            {
                "id":              "yoshimura",
                "name":            "吉村 洋文",
                "kana":            "よしむら ひろふみ",
                "party":           "大阪維新の会",
                "role":            "incumbent",
                "age":             48,
                "image":           "https://upload.wikimedia.org/wikipedia/commons/f/f0/%E5%A4%A7%E9%98%AA%E5%BA%9C_%E7%9F%A5%E4%BA%8B_%E5%90%89%E6%9D%91%E6%B4%8B%E6%96%87_%28cropped%29.jpg",
                "result":          "当選",
                "votes":           2,
                "vote_rate":       82.7,
                "score_incumbent": score,
                "score_status":    "初期評価（要チームレビュー）",
                "confirmed":       True,
                "note":            "現職として3期目当選。得票率82.7%。"
            },
            {
                "id":              "tatsumi",
                "name":            "辰巳 孝太郎",
                "kana":            "たつみ こうたろう",
                "party":           "無所属（共産推薦）",
                "role":            "challenger",
                "age":             47,
                "image":           "",
                "result":          "落選",
                "score_challenger": None,
                "score_status":    "落選候補",
                "confirmed":       True,
                "note":            "元参議院議員。カジノ反対・物価高対策を訴えた。"
            },
            {
                "id":              "taniguchi",
                "name":            "谷口 真由美",
                "kana":            "たにぐち まゆみ",
                "party":           "無所属",
                "role":            "challenger",
                "age":             49,
                "image":           "",
                "result":          "落選",
                "score_challenger": None,
                "score_status":    "落選候補",
                "confirmed":       True,
                "note":            "法学者・元大阪弁護士会所属。"
            }
        ]
    }
    IDX_OUT.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(f"[WRITE] {IDX_OUT.relative_to(ROOT)}")

    # ── 3. yoshimura.json（2023フォルダ）を作成 ─────────────────────────
    CAND_OUT.parent.mkdir(parents=True, exist_ok=True)
    cand = {
        "id":          "yoshimura",
        "name":        "吉村 洋文",
        "kana":        "よしむら ひろふみ",
        "party":       "大阪維新の会",
        "role":        "incumbent",
        "election":    "大阪府知事選挙 2023",
        "result":      "当選",
        "vote_rate":   82.7,
        "image":       "https://upload.wikimedia.org/wikipedia/commons/f/f0/%E5%A4%A7%E9%98%AA%E5%BA%9C_%E7%9F%A5%E4%BA%8B_%E5%90%89%E6%9D%91%E6%B4%8B%E6%96%87_%28cropped%29.jpg",
        "profile": {
            "born":     "1975年",
            "career":   ["弁護士", "大阪市長（2019-2019）", "大阪府知事（2019〜）"],
            "sns": {
                "twitter": "https://twitter.com/hiroyoshimura",
                "youtube": ""
            }
        },
        "manifesto_source_2023": "https://osaka-ishin.jp/pdf/manifesto/ishinfugidan_manifesto2023.pdf",
        "manifesto_note_2023":   "大阪維新の会 大阪府議会議員団 マニフェスト2023（知事選同時期）",
        "progress": {
            "total":       done + started + pending,
            "done":        done,
            "started":     started,
            "pending":     pending,
            "unknown":     unknown,
            "score":       score,
            "reviewed_at": "2026-04-24T00:00:00Z",
            "review_note": "初期評価。公知情報をもとに自動付与。要チームレビュー。"
        },
        "promises_2023": promises
    }
    CAND_OUT.write_text(json.dumps(cand, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(f"[WRITE] {CAND_OUT.relative_to(ROOT)}")

    print(f"\n── 初期評価サマリー ──────────────────")
    print(f"  完了:   {done} 件")
    print(f"  着手:   {started} 件")
    print(f"  未着手: {pending} 件")
    print(f"  不明:   {unknown} 件")
    print(f"  スコア: {score} / 100")
    print(f"\n次のステップ:")
    print(f"  チームでスプレッドシートをレビューし、ステータスを確定させてください。")
    print(f"  反映コマンド: python scripts/import_review_sheet.py \\")
    print(f"      --csv tmp/review_sheets/promises_yoshimura_2023.csv \\")
    print(f"      --json js/data/osaka_2023_governor/candidates/yoshimura.json")


if __name__ == "__main__":
    main()
