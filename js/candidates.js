// 候補者のデータを「リスト」として管理します
const candidates = [
    {
        id: 1,
        name: "町田 太郎",
        age: 64,
        party: "現職",
        status: "3期目",
        image: "https://api.dicebear.com/7.x/avataaars/svg?seed=Taro",
        desc: "「継続と安定」を掲げる3期目。駅前再開発の完遂を目指す。",
        score_manifesto: 75,
        score_consistency: 40,
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
        score_manifesto: null, // 実績がない場合は null
        score_consistency: 92,
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
        score_manifesto: null,
        score_consistency: 88,
        url: "#"
    }
];