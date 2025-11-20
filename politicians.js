// 政治家個人のデータベース
const politicians = [
    {
        id: 1,
        name: "蓮舫", // 実在の人物例
        kana: "れんほう",
        party: "立憲民主党",
        // 画像はダミー（DiceBear）です。本番はちゃんとした写真に変えます
        icon: "https://api.dicebear.com/7.x/avataaars/svg?seed=Renho", 
        type: "sangiin", // 参議院
        area: "東京都", 
        
        // polimiru独自の指標
        manifesto_rate: 85, // 公約達成率
        consistency_rate: 90, // 言動一致度
        
        // ひとこと紹介
        desc: "行政刷新の実績を強調。「7つのゼロ」の検証を推進中。",
        
        // 詳細ページへのリンク（今は#）
        url: "#"
    },
    {
        id: 2,
        name: "中川 雅治", // 実在の人物例
        kana: "なかがわ まさはる",
        party: "自民党",
        icon: "https://api.dicebear.com/7.x/avataaars/svg?seed=Nakagawa",
        type: "sangiin",
        area: "東京都",
        
        manifesto_rate: 60,
        consistency_rate: 75,

        desc: "環境大臣などを歴任。経済再生と環境政策の両立を掲げる。",
        url: "#"
    },
    {
        id: 3,
        name: "音喜多 駿", // 実在の人物例
        kana: "おときた しゅん",
        party: "日本維新の会",
        icon: "https://api.dicebear.com/7.x/avataaars/svg?seed=Otokita",
        type: "sangiin",
        area: "東京都",
        
        manifesto_rate: 70,
        consistency_rate: 88,

        desc: "規制改革と現役世代への投資を主張。ブロガー出身。",
        url: "#"
    }
];