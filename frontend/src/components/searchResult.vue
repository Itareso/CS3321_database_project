<template>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a href="./"><img src="../assets/img/logo-B.png" alt="LOGO" style="width: 35px !important;"></a>
            &nbsp;&nbsp;&nbsp;
            <a class="navbar-brand" href="./"><i class="mr-2"></i><strong>Book</strong> Hub</a>
            <button class="navbar-toggler collapsed" type="button" data-toggle="collapse" data-target="#navbarColor02"
                aria-controls="navbarColor02" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="navbar-collapse collapse" id="navbarColor02" style="">
                <!-- <ul class="navbar-nav mr-auto d-flex align-items-center">
                    <li class="nav-item">
                        <a class="nav-link" href="./">首页</a>
                    </li>
                </ul> -->


                <!-- </div> -->


                <!-- nav 中的搜索框 -->
                <div class="container" style="padding-left: 20px; padding-right: 0px;">
                    <div class="col d-flex">

                        <!-- 上方 -->
                        <div class="input-group under_border">
                            <!-- 搜索框 -->
                            <input id="search-input" type="text" class="form-control form-control-rounded no_box_shadow"
                                v-model="search_info" @keyup.enter="SearchAndGoToResultPage"
                                aria-label="Text input with dropdown button">

                            <!-- 搜索条件选择器 -->
                            <!-- BUG: 只能下拉一次菜单 选择后无法再次选择 -->
                            <div class="input-group-append">
                                <button class="btn btn-outline-secondary_rewrite dropdown-toggle btn-rounded"
                                    type="button" data-toggle="dropdown" aria-expanded="false">{{ new_search_type_print
                                    }}</button>
                                <div class="dropdown-menu">
                                    <a class="dropdown-item"
                                        @click="selectSearchType('Recommend')"><strong>Recommend</strong></a>
                                    <div role="separator" class="dropdown-divider"></div>
                                    <a class="dropdown-item"
                                        @click="selectSearchType('Title')"><strong>Title</strong></a>
                                    <a class="dropdown-item"
                                        @click="selectSearchType('Author')"><strong>Author</strong></a>
                                </div>
                            </div>
                        </div>


                        <!-- 下方 -->
                        <!-- 搜索按钮 -->
                        <div class="col">
                            <button type="button" @click="SearchAndGoToResultPage"
                                class="btn btn-primary btn-rounded button_white_border_search">Search</button>
                        </div>
                    </div>
                </div>
            </div>

            <ul class="navbar-nav ml-auto d-flex align-items-center">
                <li v-if="!this.isLogin" class="nav-item">
                    <span class="nav-link">
                        <a class="btn btn-secondary btn-round fade-down-left" href="/signup">注册</a>&nbsp;
                        <a class="btn btn-secondary btn-round " href="/login">登录</a>
                    </span>
                </li>
                <li v-else class="nav-item">
                    <span class="nav-link">
                        <a class="btn btn-outline-primary btn-round fade-down-left"
                            style="color:#c3a6cb !important; border-color: #c3a6cb !important;" @click="logOut">登出</a>
                    </span>
                </li>
            </ul>
        </div>


    </nav>

    <div>
        <div class="row align-items-center justify-content-center text-center">
            <div class="col-md-10">
            </div>
        </div>
        <br><br>

        <!-- <div class="media" v-for="(paper, key) in response_data" :key='key'>
                <img src="../assets/img/N.png" class="marigin_lr" alt="..." :width="30">
                <div class="media-body">
                    <h5 class=""><span v-html="paper.title[0]"></span></h5>
                    <p><strong>Abstract :</strong>&nbsp; <span v-html="paper.abstract"></span></p>
                </div>
            </div> -->


        <div class="media" v-for="(book, key) in response_data" :key='key'>
            <!-- key 没用, key 是0/1/2... 的序号 -->
            <div class=" bg-light reform_size_frame">
                <div class="container-fluid reform_size_container">
                    <div class="row justify-content-between align-items-center text-md-center text-lg-left">

                        <div class="reform_size_content" :class="{ 'col-lg-9': book.pic_num !== 0 }">
                            <h5 class="text-black hoverable cursor_pointer">
                                <strong><span @click="GoToPaperPage(book.douban_id)"
                                        v-html="htmlLatex(book.title)"></span></strong>
                                &nbsp;&nbsp;
                            </h5>
                            <button v-if="!book.stared" @click="starBook(book.douban_id, key)"
                                class="btn btn-outline-primary" type="button">收藏
                            </button>
                            <button v-else @click="starBook(book.douban_id, key)" class="btn btn-primary" type="button">取消收藏
                            </button>

                            <p v-if="book.tag != null && book.tag != ''"><span
                                    class="badge badge-primary">类别</span>&nbsp;
                                <span class="badge badge-success" v-html="book.tag"></span>
                            </p>

                            <p v-if="book.authors.some(person => person.role === '作者')">
                                <span class="badge badge-primary">作者</span>&nbsp;
                                <span v-for="(person, index) in book.authors" :key="index">
                                    <span v-if="index > 0 && person.role == '作者'"><strong>&nbsp;|&nbsp;</strong>
                                    </span>
                                    <span v-if="person.role == '作者'" @click="SearchAuthor(person.name)"
                                        class="color_blue font-weight-bold hoverable cursor_pointer"
                                        v-html="person.name">
                                    </span>
                                </span>
                            </p>
                            <p v-else>
                                <span class="badge badge-primary">作者</span>&nbsp;
                                <span><b>暂无</b></span>
                            </p>

                            <p>
                                <span class="badge badge-primary">简介</span>&nbsp;
                                <span v-if="book.related_intro"
                                    v-html="htmlLatex(getDisplayIntroText(book, key))"></span>
                                <span v-else><b>暂无</b></span>

                                <button v-if="book.related_intro && shouldShowToggleButton(book)"
                                    @click="toggleIntroExpansionForItem(key)" class="btn btn-link btn-sm p-0 ml-1"
                                    type="button" style="vertical-align: baseline; text-decoration: none;">
                                    {{ expandedIntroStates[key] ? '收起' : '展开' }}
                                </button>
                            </p>

                            <p v-if="book.bookInfo.ISBN != null && book.bookInfo.ISBN != ''"><span
                                    class="badge badge-primary">ISBN</span>&nbsp;
                                <span @click="copyLink(book.bookInfo.ISBN, key)"
                                    :class="'copy-button copy-button-' + key" data-container="body"
                                    data-toggle="popover" data-placement="top" data-content="已复制ISBN号">
                                    <span class="badge btn-outline-purple cursor_pointer"
                                        v-html="book.bookInfo.ISBN"></span>
                                </span>
                            </p>

                        </div>

                        <!-- 书籍封面展示 -->
                        <div class="col-lg-3 text-md-right text-lg-right mt-4 mb-4">
                            <div :id="'paperPictureDisplay' + key" class="carousel slide" data-ride="carousel">
                                <div class="carousel-inner">
                                    <img :src="'' + book.img_link" class="img-fluid mx-auto d-block fill-image">
                                </div>
                            </div>
                        </div>

                    </div>
                </div>
            </div>
        </div>

        <div v-if="response_data.length > 0" class="alert alert-cyan text_center" role="alert">
            <strong>已显示全部搜索结果</strong>
        </div>

        <div v-else class="alert alert-cyan text_center" role="alert">
            <strong>无搜索结果，换一个关键词试试吧</strong>
        </div>

    </div>
</template>

<script>
import axios from 'axios';
import ClipboardJS from 'clipboard';
import katex from 'katex';

export default {
    data() {
        return {
            isLogin: false,

            new_search_type: "recommend",
            new_search_type_print: "Recommend",

            search_field: "havnt_search",
            search_field_print: "havnt_search",

            search_info: "",
            search_source: "",

            paper_number: 30,

            agreed: false,
            searchArxiv: false,

            already_searched: false,
            paper_id: "NULL",
            paper_title: "NULL",
            paper_abstract: "NULL",

            responses: [],
            response_data: [],

            pictures_urls: {},

            expandedIntroStates: {},
            introMaxLength: 210,
        }
    },

    async mounted() {
        const meta = document.createElement('meta');
        meta.name = 'referrer';
        meta.content = 'no-referrer';
        document.head.appendChild(meta);
        await this.initialize();
    },

    methods: {

        async initialize() {
            await this.checkLogin();
            console.log("initializing...")
            $(this.$el).find('[data-toggle="dropdown"]').dropdown();
            this.search_field = this.$route.query.field;
            this.search_field_print = this.new_search_type_print;
            console.log("old search field: " + this.search_field);

            this.new_search_type = this.search_field;
            this.new_search_type_print = this.search_field.charAt(0).toUpperCase() + this.search_field.slice(1);

            console.log("new search type: " + this.new_search_type);
            console.log("new search type print: " + this.new_search_type_print);

            this.search_info = this.$route.query.info;
            this.agreed = this.searchArxiv;

            console.log("field = " + this.search_field);
            console.log("info = " + this.search_info);
            this.getAllPaperInfo();
            $(function () {
                $('[data-toggle="popover"]').popover();
            });
        },

        SearchAndGoToResultPage() {
            var url = "/searchResult?field=" + this.new_search_type + "&info=" + encodeURIComponent(this.search_info);
            this.$router.push(url);
            this.initialize();
        },

        changeAgreement() {
            this.agreed = !this.agreed;
            this.searchArxiv = !this.searchArxiv;
            // console.log("agreed changed to " + this.agreed);
            console.log("searchArxiv changed to " + this.searchArxiv);
        },

        selectSearchType(type) {
            this.new_search_type_print = type;
            this.$nextTick(() => {
                $(this.$el).find('[data-toggle="dropdown"]').dropdown('update');
            });
            this.new_search_type = type.toLowerCase();
            console.log("search_type changed to " + type);
            console.log("search_type_print: " + type);
        },

        getAllPaperInfo() {
            // axios.get('http://10.80.158.19:8088/api/v1/search', {
            axios.get('http://10.80.158.19:8088/api/v1/search', {
                params: {
                    field: this.search_field,
                    info: this.search_info,
                }
            })
                .then((response) => {
                    this.responses = response;
                    this.response_data = response.data;
                    console.log("Search results data number: " + this.response_data.length);
                })
                .catch((error) => {
                    console.error('Error:', error);
                    this.already_searched = true;
                    this.paper_id = "!! ERROR !!";
                });
        },


        // getLimitedPaperInfo() {
        //     response_data = Object.fromEntries(Object.entries(this.responses.data).slice(0, this.paper_number));
        //     // 打印response_data长度
        //     console.log(Object.keys(response_data).length);
        // },


        starBook(_id, key) {
            axios.get('http://10.80.158.19:8088/api/v1/user/star', {
                params: {
                    id: _id,
                }
            })
                .then(response => {
                    // 处理返回的 response.data
                    console.log('Response Data:', response.data);
                    if (response.data.action == "added") {
                        this.response_data[key].stared = true;
                    } else if (response.data.action == "removed") {
                        this.response_data[key].stared = false;
                    }
                })
                .catch(error => {
                    // 处理错误
                    console.error('Error:', error);
                });
        },

        SearchAuthor(_name) {
            var _url = "/searchResult?field=author" + "&info=" + encodeURIComponent(_name);
            window.open(_url, "_blank");
        },

        GoToPaperPage(_ID) {
            const _url = "/book?id=" + _ID;
            window.open(_url, "_blank");
        },

        copyLink(_doi, key) {
            const textToCopy = _doi;
            const selector = '.copy-button-' + key;
            const clipboard = new ClipboardJS(selector, {
                text: () => textToCopy
            });

            clipboard.on('success', () => {

                const temp = '[data-toggle="popover"]';
                $(temp).popover();
                const popoverElement = $(selector);

                popoverElement.popover('show');

                setTimeout(() => {
                    popoverElement.popover('hide');
                }, 1000); // 1秒后隐藏 popover
            });

            clipboard.onClick({
                target: document.querySelector(selector)
            });
        },

        async checkLogin() {
            return axios.get('http://10.80.158.19:8088/api/v1/user/check_login')
                .then((response) => {
                    this.isLogin = response.data.login_in;
                    console.log("log in status: " + response.data.login_in);
                })
                .catch((error) => {
                    console.log(error);
                })
        },

        async logOut() {
            axios.get('http://10.80.158.19:8088/api/v1/user/logout')
                .then((response) => {
                    console.log("log out status: " + response.data.logout);
                    this.isLogin = false;

                })
                .catch((error) => {
                    console.log(error);
                });
            await this.initialize();
        },

        htmlLatex(text) {
            if (typeof text !== 'string') {
                console.log("null latex");
                return '';
            }

            const regex = /(\$\$?[^$]+\$?\$)/g;
            // const text = _t;
            let lastIndex = 0;
            let result = '';

            text.replace(regex, (match, tex, index) => {
                result += text.slice(lastIndex, index);
                const latex = tex.slice(tex.startsWith('$$') ? 2 : 1, tex.endsWith('$$') ? -2 : -1);

                // Create a dummy div element to parse the HTML string
                const dummyDiv = document.createElement('div');
                dummyDiv.innerHTML = katex.renderToString(latex, { throwOnError: false });

                // Remove the <span class="katex-html"> element
                const katexHtml = dummyDiv.querySelector('.katex-html');
                if (katexHtml) {
                    katexHtml.remove();
                }

                // Append the modified HTML to the result
                result += dummyDiv.innerHTML;

                lastIndex = index + tex.length;
                return match;
            });

            result += text.slice(lastIndex);
            return result;
        },

        getDisplayIntroText(book, itemKey) {
            if (!book || !book.related_intro) {
                return '';
            }
            const fullRawIntro = String(book.related_intro);
            // !!this.expandedIntroStates[itemKey] 会将 undefined 转换为 false
            const isExpanded = !!this.expandedIntroStates[itemKey];

            if (isExpanded || fullRawIntro.length <= this.introMaxLength) {
                return fullRawIntro;
            } else {
                return fullRawIntro.substring(0, this.introMaxLength) + "...";
            }
        },

        shouldShowToggleButton(book) {
            if (!book || !book.related_intro) {
                return false;
            }
            return String(book.related_intro).length > this.introMaxLength;
        },

        toggleIntroExpansionForItem(itemKey) {
            this.expandedIntroStates[itemKey] = !(this.expandedIntroStates[itemKey] || false);
        }
    },

    watch: {
        '$route': {
            immediate: true,
            handler() {
                this.initialize();
            }
        },
    },

    computed: {

    }

}


</script>


<style>
.marigin_lr {
    margin-left: 1rem;
    margin-right: 2rem;
}

.reform_size_frame {
    width: 90% !important;
    margin-bottom: 10px !important;
    margin: 0 auto;
    padding-top: 10px;
}

.reform_size_container {
    width: 90% !important;
    margin-top: 15px !important;
    margin-left: 2% !important;
    margin-right: 1% !important;
    margin: 0 0 10px 0;
}

.reform_size_content {
    width: 100% !important;
    height: auto !important;
}

.reform_img_button {
    position: absolute !important;
    top: 30% !important;
    height: 30px !important;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 5px !important;
    text-align: center;
    opacity: 0.5;
}

.button-right {
    right: 0 !important;
}

.button-left {
    left: 0 !important;
}

.paper_title {
    font-size: 20px;
}

.hoverable:hover {
    text-decoration: underline;
}

.fill-image {
    object-fit: cover;
    width: 500px;
    height: 200px;
    padding: 10px;
}

.color_blue {
    color: #2578b5;
}

.color_purple {
    color: #8d4bbb;
}

.text_center {
    text-align: center !important;
    width: auto !important;
    margin-left: 70.852px;
    margin-right: 70.852px;
    margin-top: 10px;
    margin-bottom: 200px;
    background-color: #2578b5;
    color: #ffffff;
    border: none;
}

.cursor_pointer {
    cursor: pointer;
}

.button_white_border_search {
    border-color: #ffffff;
    top: 45%;
    transform: translate(-50%, -50%);
    right: -50%;
}

.badge_outline {
    border: 1px solid #2578b5 !important;
    color: black !important;
}

.dropdown {
    position: relative;
    display: inline-block;
}

.dropdown-menu {
    position: absolute;
    top: 100%;
    /* Position below the button */
    left: 0;
    z-index: 1000;
    /* Ensure it's above other content */
    display: none;
    /* Initially hidden */
}

.dropdown:hover .dropdown-menu {
    display: block;
    /* Show on hover */
}
</style>
