// 政治家個人のデータベース
// url が設定されているものだけ検索結果に表示される
const politicians = [
    {
        id: "takaichi-sanae",
        name: "高市 早苗",
        kana: "たかいち さなえ",
        party: "自民党",
        role: "第104・105代 内閣総理大臣",
        area: "奈良2区（11選）",
        photo: "https://upload.wikimedia.org/wikipedia/commons/3/32/Sanae_Takaichi_portrait_%28HD%29_%28cropped_1%29.jpg",
        url: "politicians/takaichi-sanae/index.html",
        tags: ["高市", "高市早苗", "経済安保", "積極財政", "防衛", "奈良", "自民党", "サナエノミクス", "たかいち", "神戸大学", "松下政経塾"],
        desc: "神戸大学経営学部卒、松下政経塾を経て国政へ。総務大臣、経済安全保障担当大臣、自民党政調会長などを歴任。"
    },
    {
        id: "yoshimura-hirofumi",
        name: "吉村 洋文",
        kana: "よしむら ひろふみ",
        party: "大阪維新の会",
        role: "大阪府知事",
        area: "大阪府",
        photo: "https://upload.wikimedia.org/wikipedia/commons/f/f0/%E5%A4%A7%E9%98%AA%E5%BA%9C_%E7%9F%A5%E4%BA%8B_%E5%90%89%E6%9D%91%E6%B4%8B%E6%96%87_%28cropped%29.jpg",
        url: "politicians/yoshimura-hirofumi/index.html",
        tags: ["吉村", "吉村洋文", "よしむら", "大阪府知事", "大阪維新の会", "維新", "大阪市長", "九州大学", "公約達成度"],
        desc: "九州大学法学部卒、弁護士を経て大阪市会議員、衆議院議員、大阪市長、大阪府知事を歴任。2023年府政公約の達成度を蓄積。"
    },
    {
        id: "aso-taro",
        name: "麻生 太郎",
        kana: "あそう たろう",
        party: "自民党",
        role: "副総裁",
        area: "福岡8区",
        photo: "https://www.jimin.jp/member/img/asou-tarou.jpg",
        url: "politicians/aso-taro/index.html",
        tags: ["麻生", "麻生太郎", "あそう", "自民党", "副総裁", "総理大臣", "財務大臣", "福岡"],
        desc: "第92代内閣総理大臣、財務大臣、外務大臣、党幹事長などを歴任。"
    },
    {
        id: "suzuki-shunichi",
        name: "鈴木 俊一",
        kana: "すずき しゅんいち",
        party: "自民党",
        role: "幹事長",
        area: "岩手2区",
        photo: "https://www.jimin.jp/member/img/suzuki-shunichi.jpg",
        url: "politicians/suzuki-shunichi/index.html",
        tags: ["鈴木", "鈴木俊一", "すずき", "自民党", "幹事長", "財務大臣", "岩手"],
        desc: "財務大臣、総務会長、環境大臣などを歴任。高市体制の幹事長。"
    },
    {
        id: "kobayashi-takayuki",
        name: "小林 鷹之",
        kana: "こばやし たかゆき",
        party: "自民党",
        role: "政務調査会長",
        area: "千葉2区",
        photo: "https://www.jimin.jp/member/img/kobayashi-takayuki.jpg",
        url: "politicians/kobayashi-takayuki/index.html",
        tags: ["小林", "小林鷹之", "こばやし", "自民党", "政調会長", "政務調査会長", "経済安全保障", "千葉"],
        desc: "経済安全保障担当大臣などを歴任。政務調査会長として政策立案を担う。"
    },
    {
        id: "arimura-haruko",
        name: "有村 治子",
        kana: "ありむら はるこ",
        party: "自民党",
        role: "総務会長",
        area: "比例代表",
        photo: "https://www.jimin.jp/member/img/arimura-haruko.jpg",
        url: "politicians/arimura-haruko/index.html",
        tags: ["有村", "有村治子", "ありむら", "自民党", "総務会長", "参議院", "比例"],
        desc: "女性活躍・行政改革・少子化対策などの担当大臣を歴任。"
    },
    {
        id: "furuya-keiji",
        name: "古屋 圭司",
        kana: "ふるや けいじ",
        party: "自民党",
        role: "選挙対策委員長",
        area: "岐阜5区",
        photo: "https://www.jimin.jp/member/img/furuya-keiji.jpg",
        url: "politicians/furuya-keiji/index.html",
        tags: ["古屋", "古屋圭司", "ふるや", "自民党", "選対委員長", "選挙対策委員長", "拉致問題", "岐阜"],
        desc: "国家公安委員長、拉致問題担当大臣、防災担当大臣などを歴任。"
    },
    {
        id: "tamaki-yuichiro",
        name: "玉木 雄一郎",
        kana: "たまき ゆういちろう",
        party: "国民民主党",
        role: "代表",
        area: "香川2区",
        photo: "https://new-kokumin.jp/wp-content/uploads/2020/11/member_img3.jpg",
        url: "politicians/tamaki-yuichiro/index.html",
        tags: ["玉木", "玉木雄一郎", "たまき", "国民民主党", "代表", "手取りを増やす", "年収の壁", "178万円", "ガソリン暫定税率", "香川", "高松高校", "東京大学", "ハーバード", "財務省"],
        desc: "香川県立高松高校、東京大学法学部、ハーバード大学大学院を経て大蔵省・財務省へ。国民民主党代表として年収の壁178万円、ガソリン暫定税率廃止などを追う。"
    },
    {
        id: "furukawa-motohisa",
        name: "古川 元久",
        kana: "ふるかわ もとひさ",
        party: "国民民主党",
        role: "代表代行",
        area: "愛知2区",
        photo: "https://new-kokumin.jp/wp-content/uploads/2020/11/member_img5.jpg",
        url: "politicians/furukawa-motohisa/index.html",
        tags: ["古川", "古川元久", "ふるかわ", "国民民主党", "代表代行", "国対", "愛知", "東大", "大蔵省"],
        desc: "国家戦略担当大臣、経済財政政策担当大臣などを歴任。"
    },
    {
        id: "shimba-kazuya",
        name: "榛葉 賀津也",
        kana: "しんば かづや",
        party: "国民民主党",
        role: "幹事長",
        area: "静岡県",
        photo: "https://new-kokumin.jp/wp-content/uploads/2024/08/83adbecc191cd73da251eeec6cf245c0-scaled-e1738200045606.jpg",
        url: "politicians/shimba-kazuya/index.html",
        tags: ["榛葉", "榛葉賀津也", "しんば", "国民民主党", "幹事長", "防衛副大臣", "外務副大臣", "静岡"],
        desc: "防衛副大臣、外務副大臣を歴任。国民民主党幹事長。"
    },
    {
        id: "funayama-yasue",
        name: "舟山 康江",
        kana: "ふなやま やすえ",
        party: "国民民主党",
        role: "参議院議員会長",
        area: "山形県",
        photo: "https://new-kokumin.jp/wp-content/uploads/2020/11/member_img14.jpg",
        url: "politicians/funayama-yasue/index.html",
        tags: ["舟山", "舟山康江", "ふなやま", "国民民主党", "参議院議員会長", "両院議員総会長", "農林水産省", "山形"],
        desc: "農林水産省出身。党政調会長を経て参議院議員会長兼両院議員総会長。"
    },
    {
        id: "hamaguchi-makoto",
        name: "浜口 誠",
        kana: "はまぐち まこと",
        party: "国民民主党",
        role: "政務調査会長",
        area: "比例区",
        photo: "https://new-kokumin.jp/wp-content/uploads/2021/03/bf7c646c5acc33a00f095dc8ec02c885.jpg",
        url: "politicians/hamaguchi-makoto/index.html",
        tags: ["浜口", "浜口誠", "はまぐち", "国民民主党", "政調会長", "政務調査会長", "自動車総連", "トヨタ", "比例"],
        desc: "トヨタ自動車、自動車総連での経験を持つ参議院議員。政務調査会長。"
    }
];

window.politicians = politicians;
