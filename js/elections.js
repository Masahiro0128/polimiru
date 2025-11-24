// 選挙データを管理するリスト
const elections = [
    {
        id: 1,
        title: "町田市長選挙 2026",
        category: "local",
        date: "2026年2月XX日 投票",
        prefecture: "東京都",
        desc: "再開発、給食、子育て支援...。<br>現職の実績と新人の公約を徹底比較。",
        image: "",   // ← ここを空にして東京都の共通画像（東京タワー）を使用
        url: "elections/machida.html",
        badgeType: "local",
        status: "2026年 注目"
    },
    {
        id: 4, 
        title: "第27回 参議院議員選挙（東京）",
        category: "national",
        date: "2025年7月 予定",
        prefecture: "東京都",
        desc: "首都決戦。定数6を巡る各党の攻防。<br>公約達成率で現職を評価。",
        image: "",   // ← **東京都はこっちも空に**（東京タワーに統一される）
        url: "elections/sangiin_tokyo.html",
        badgeType: "national", 
        status: "2025年 注目"
    },
    {
        id: 2,
        title: "長崎県知事選挙",
        category: "local",
        date: "2026年2月 予定",
        prefecture: "長崎県",
        desc: "石木ダム問題の行方は？<br>県政の長期的な課題を検証します。",
        image: "https://images.unsplash.com/photo-1565627788441-4942d2302d7c?auto=format&fit=crop&w=500&q=80",
        url: "#",
        badgeType: "local",
        status: "予定"
    },
    {
        id: 3,
        title: "第5X回 衆議院議員総選挙",
        category: "national",
        date: "202X年 終了",
        prefecture: "国政",
        desc: "各党のマニフェスト達成状況を追跡。<br>当選議員のその後の活動をチェック。",
        image: "https://images.unsplash.com/photo-1529101091760-6149976f1581?auto=format&fit=crop&w=500&q=80",
        url: "#",
        badgeType: "national",
        status: "アーカイブ"
    },
    {
        id: 10,
        title: "大阪府知事選挙 2023",
        category: "local",
        date: "2023年4月9日 投開票（終了）",
        prefecture: "大阪府",
        desc: "万博・IR誘致の是非と、維新府政への評価が問われた選挙。<br>公約達成度の最終評価を公開。",
        image: "",   // 大阪も空（prefectureImages の osaka.jpg が反映）
        url: "elections/osaka/2023_governor/index.html",
        badgeType: "local",
        status: "アーカイブ"
    }
];
