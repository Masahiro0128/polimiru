// 候補者データ（一般ユーザーは overall_score しか見ない）
const candidates = [
    {
        id: 1,
        name: "町田 太郎",
        age: 64,
        party: "現職",
        status: "3期目",
        image: "https://api.dicebear.com/7.x/avataaars/svg?seed=Taro",
        desc: "「継続と安定」を掲げる3期目。駅前再開発の完遂を目指す。",

        // 🔥 表に出すのはこれだけ（100点満点）
        overall_score: 74,

        // 🔧 内部スコア（methodology ページ用）
        scores: {
            manifesto: 75,       // 言行一致度（現職のみ）
            consistency: 40,      // 一貫性（新人にも現職にも使える）
            specificity: 0.62,    // PSI（公約の具体性）0〜1
            feasibility: 0.58     // 実現可能性F（0〜1）
        },

        url: "../detail.html"
    },

    {
        id: 2,
        name: "相模 花子",
        age: 42,
        party: "新人",
        status: "元市議",
        image: "https://api.dicebear.com/7.x/avataaars/svg?seed=Hanako",
        desc: "子育て支援の拡充を主張。現市政の財政規律を批判。",

        overall_score: 81, // ← 表示すべきスコア

        scores: {
            manifesto: null,     // 新人なので無し
            consistency: 92,
            specificity: 0.71,
            feasibility: 0.63
        },

        url: "#"
    },

    {
        id: 3,
        name: "玉川 太郎",
        age: 55,
        party: "新人",
        status: "IT起業家",
        image: "https://api.dicebear.com/7.x/avataaars/svg?seed=Jiro",
        desc: "行政のDX化を推進。AIを活用した予算配分を提案。",

        overall_score: 78,

        scores: {
            manifesto: null,
            consistency: 88,
            specificity: 0.66,
            feasibility: 0.59
        },

        url: "#"
    }
];
