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

// （既存の candidates 配列の中に追記、または既存の後に以下を追加）

// ★以下のデータを candidates 配列の中に追加してください
// もし既存のデータがある場合は、カンマ(,)で区切って続けて書いてください。

/* 既存のデータ... , 
*{
        id: 'osaka_yoshimura',
        electionId: 'osaka2023', // ここで町田と区別します
        name: '吉村 洋文',
        party: '大阪維新の会',
        status: '現職',
        age: 47,
        image: 'https://images.unsplash.com/photo-1556157382-97eda2d62296?auto=format&fit=crop&w=400&q=80', // イメージ画像
        url: '#',
        desc: '「府市一体」の改革を継続し、2025年万博の成功とIR誘致を推進。教育無償化を公約の柱に掲げる。',
        score_manifesto: 88,  // 公約の具体性
        overall_score: 85     // 実績スコア（高い設定）
    },
    {
        id: 'osaka_tatsumi',
        electionId: 'osaka2023',
        name: '辰巳 孝太郎',
        party: '無所属（共産推薦）',
        status: '新人',
        age: 46,
        image: 'https://images.unsplash.com/photo-1542596594-649edbc13630?auto=format&fit=crop&w=400&q=80',
        url: '#',
        desc: 'カジノ誘致の即時中止を主張。物価高対策や中小企業支援、ケア労働者の賃上げを訴える。',
        score_manifesto: 72,
        overall_score: 70
    },
    {
        id: 'osaka_taniguchi',
        electionId: 'osaka2023',
        name: '谷口 真由美',
        party: '無所属',
        status: '新人',
        age: 48,
        image: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=400&q=80',
        url: '#',
        desc: '「アップデートOSAKA」を掲げ、対話重視の府政への転換を主張。IR誘致には慎重姿勢を示す。',
        score_manifesto: 76,
        overall_score: 74
        }