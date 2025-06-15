<template>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a href="/"><img src="../assets/img/logo-B.png" alt="LOGO" style="width: 35px !important;"></a>
            &nbsp;&nbsp;&nbsp;
            <a class="navbar-brand" href="./"><i class="mr-2"></i><span style="font-weight: bold">Book</span> Hub</a>
            <button class="navbar-toggler collapsed" type="button" data-toggle="collapse" data-target="#navbarColor02"
                aria-controls="navbarColor02" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="navbar-collapse collapse" id="navbarColor02" style="">
                <ul class="navbar-nav mr-auto d-flex align-items-center">
                    <li class="nav-item">
                        <a class="nav-link" href="./" style="font-weight: none; font-size: 15px">首页</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="./searchresult" style="font-weight: none; font-size: 15px">发现</a>
                    </li>
                </ul>
                <ul class="navbar-nav ml-auto d-flex align-items-center">
                    <li class="nav-item">
                    </li>
                </ul>
            </div>


            <ul class="navbar-nav ml-auto d-flex align-items-center">
                <li class="nav-item">
                    <a class="nav-link" href="./reader" style="font-weight: none; font-size: 15px">我的书架</a>
                </li>
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


    <div class="jumbotron jumbotron-fluid set_margin set_padding">
        <div class="container mt-4">
            <!-- 上半部分：左右布局 -->
            <div class="d-flex flex-row">
                <!-- 左侧图片 -->
                <div style="margin-right: 20px;">
                    <img :src="this.book_img_link" alt="Book Cover"
                        style="width: 150px; height: auto; border-radius: 8px;">
                </div>

                <!-- 右侧文字内容 -->
                <div style="flex: 1;">
                    <h2 class="text-left">
                        {{ this.book_title }}&nbsp;
                        <span class="badge reform_badge_solid">{{ this.book_tag }}</span>
                        &nbsp;<span class="badge reform_badge_outline">{{ this.book_publish_year }}</span>
                    </h2>

                    <!-- 作者部分 -->
                    <p class="lead">
                        <span class="badge badge-primary">作者</span>&nbsp;
                        <span v-for="(person, i) in book_authors.filter(p => p.role === '作者')" :key="person.douban_id">
                            <span v-if="showAllAuthors || i < 10" @click="SearchAuthor(person.name)"
                                class="color_blue font-weight-bold hoverable cursor_pointer">{{ person.name }}</span>
                            <span
                                v-if="(showAllAuthors || i < 10) && i !== book_authors.filter(p => p.role === '作者').length - 1">
                                <strong>&nbsp;|&nbsp;</strong>
                            </span>
                        </span>
                    <div class="btn btn-outline-cyan btn-sm mt-2"
                        v-if="book_authors.filter(p => p.role === '作者').length > 10"
                        @click="showAllAuthors = !showAllAuthors">
                        {{ showAllAuthors ? '收起' : '展开' }}
                    </div>
                    </p>

                    <!-- 其他角色 -->
                    <div v-for="(personGroup, role) in this.person_list" :key="role" class="mb-2">
                        <p class="lead">
                            <span class="badge badge-primary">{{ role }}</span>&nbsp;
                            <span v-for="(person, i) in personGroup" :key="person.douban_id">
                                <a :href="person.link" target="_blank" rel="noopener"
                                    class="color_blue font-weight-bold hoverable cursor_pointer">{{ person.name }}</a>
                                <span v-if="i !== personGroup.length - 1"><strong>&nbsp;|&nbsp;</strong></span>
                            </span>
                        </p>
                    </div>

                    <!-- 概述 -->
                    <p class="lead">
                        <span class="badge badge-purple">简介</span>&nbsp;
                        <span v-if="book_related_intro" v-html="book_related_intro"></span>
                        <span v-else><b>暂无</b></span>
                    </p>

                    <!-- 总评分和各项评分 -->
                    <p class="lead mt-3">
                        <span class="badge badge-warning">评分</span>&nbsp;
                        <span style="font-weight: bold; margin-right: 10px;"> {{ (this.book_total_star_rate).toFixed(2)
                        }}
                        </span>
                        <span class="total-rating-stars">
                            <span v-for="n in totalRatingFullStars" :key="'total-full-' + n"
                                :style="{ color: 'orange', fontSize: '20px', marginRight: '2px', verticalAlign: 'middle' }">★</span>

                            <span v-if="totalRatingPartialStarVisible" :style="{
                                position: 'relative',
                                display: 'inline-block',
                                fontSize: '20px',
                                lineHeight: 1,
                                marginRight: '2px',
                                verticalAlign: 'middle'
                            }">
                                <span :style="{ color: '#ccc' }">★</span> <span :style="{
                                    position: 'absolute',
                                    left: 0,
                                    top: 0,
                                    overflow: 'hidden',
                                    color: 'orange',
                                    width: totalRatingPartialStarWidth
                                }">
                                    ★ </span>
                            </span>

                            <span v-for="n in totalRatingEmptyStars" :key="'total-empty-' + n"
                                :style="{ color: '#ccc', fontSize: '20px', marginRight: '2px', verticalAlign: 'middle' }">★</span>
                        </span>
                    </p>

                    <div v-for="i in 5" :key="i" class="d-flex align-items-center"
                        style="margin-left: 60px; margin-bottom: 1px;">
                        <span style="width: 50px;">
                            {{ ((this.book_star_rate[i] ?? this.book_star_rate[i - 1] ?? 0) * 100).toFixed(1) }}%
                        </span>
                        <span v-for="n in (6 - i)" :key="n" style="color: black; font-size: 20px;">★</span>
                    </div>
                </div>
            </div>

            <!-- 下半部分：按钮组 -->
            <div class="mt-3 d-flex flex-wrap gap-2">
                <span v-if="!book_is_starred">
                    <button @click="starBook" class="btn btn-outline-primary" data-container="body"
                        data-toggle="popover2" data-placement="top" data-content="已收藏">收藏
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                            class="bi bi-share-fill" viewBox="0 0 16 16">
                            <path
                                d="M11 2.5a2.5 2.5 0 1 1 .603 1.628l-6.718 3.12a2.499 2.499 0 0 1 0 1.504l6.718 3.12a2.5 2.5 0 1 1-.488.876l-6.718-3.12a2.5 2.5 0 1 1 0-3.256l6.718-3.12A2.5 2.5 0 0 1 11 2.5z" />
                        </svg>
                    </button>
                </span>
                <span v-else>
                    <button @click="starBook" class="btn btn-outline-primary" data-container="body"
                        data-toggle="popover2" data-placement="top" data-content="已取消收藏">取消收藏
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                            class="bi bi-share-fill" viewBox="0 0 16 16">
                            <path
                                d="M11 2.5a2.5 2.5 0 1 1 .603 1.628l-6.718 3.12a2.499 2.499 0 0 1 0 1.504l6.718 3.12a2.5 2.5 0 1 1-.488.876l-6.718-3.12a2.5 2.5 0 1 1 0-3.256l6.718-3.12A2.5 2.5 0 0 1 11 2.5z" />
                        </svg>
                    </button>
                </span>
                &nbsp;&nbsp;
                <button @click="copyLink" class="copy-button btn btn-outline-primary" data-container="body"
                    data-toggle="popover" data-placement="top" data-content="已复制ISBN号">ISBN
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                        class="bi bi-share-fill" viewBox="0 0 16 16">
                        <path
                            d="M11 2.5a2.5 2.5 0 1 1 .603 1.628l-6.718 3.12a2.499 2.499 0 0 1 0 1.504l6.718 3.12a2.5 2.5 0 1 1-.488.876l-6.718-3.12a2.5 2.5 0 1 1 0-3.256l6.718-3.12A2.5 2.5 0 0 1 11 2.5z" />
                    </svg>
                </button>
                &nbsp;&nbsp;
                <a :href="getOriginWebsite()" target="_blank" class="btn btn-outline-primary">豆瓣图书
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                        class="bi bi-browser-safari" viewBox="0 0 16 16">
                        <path
                            d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16Zm.25-14.75v1.5a.25.25 0 0 1-.5 0v-1.5a.25.25 0 0 1 .5 0Zm0 12v1.5a.25.25 0 1 1-.5 0v-1.5a.25.25 0 1 1 .5 0ZM4.5 1.938a.25.25 0 0 1 .342.091l.75 1.3a.25.25 0 0 1-.434.25l-.75-1.3a.25.25 0 0 1 .092-.341Zm6 10.392a.25.25 0 0 1 .341.092l.75 1.299a.25.25 0 1 1-.432.25l-.75-1.3a.25.25 0 0 1 .091-.34ZM2.28 4.408l1.298.75a.25.25 0 0 1-.25.434l-1.299-.75a.25.25 0 0 1 .25-.434Zm10.392 6 1.299.75a.25.25 0 1 1-.25.434l-1.3-.75a.25.25 0 0 1 .25-.434ZM1 8a.25.25 0 0 1 .25-.25h1.5a.25.25 0 0 1 0 .5h-1.5A.25.25 0 0 1 1 8Zm12 0a.25.25 0 0 1 .25-.25h1.5a.25.25 0 1 1 0 .5h-1.5A.25.25 0 0 1 13 8ZM2.03 11.159l1.298-.75a.25.25 0 0 1 .25.432l-1.299.75a.25.25 0 0 1-.25-.432Zm10.392-6 1.299-.75a.25.25 0 1 1 .25.433l-1.3.75a.25.25 0 0 1-.25-.434ZM4.5 14.061a.25.25 0 0 1-.092-.341l.75-1.3a.25.25 0 0 1 .434.25l-.75 1.3a.25.25 0 0 1-.342.091Zm6-10.392a.25.25 0 0 1-.091-.342l.75-1.299a.25.25 0 1 1 .432.25l-.75 1.3a.25.25 0 0 1-.341.09ZM6.494 1.415l.13.483a.25.25 0 1 1-.483.13l-.13-.483a.25.25 0 0 1 .483-.13ZM9.86 13.972l.13.483a.25.25 0 1 1-.483.13l-.13-.483a.25.25 0 0 1 .483-.13ZM3.05 3.05a.25.25 0 0 1 .354 0l.353.354a.25.25 0 0 1-.353.353l-.354-.353a.25.25 0 0 1 0-.354Zm9.193 9.193a.25.25 0 0 1 .353 0l.354.353a.25.25 0 1 1-.354.354l-.353-.354a.25.25 0 0 1 0-.353ZM1.545 6.01l.483.13a.25.25 0 1 1-.13.483l-.483-.13a.25.25 0 1 1 .13-.482Zm12.557 3.365.483.13a.25.25 0 1 1-.13.483l-.483-.13a.25.25 0 1 1 .13-.483Zm-12.863.436a.25.25 0 0 1 .176-.306l.483-.13a.25.25 0 1 1 .13.483l-.483.13a.25.25 0 0 1-.306-.177Zm12.557-3.365a.25.25 0 0 1 .176-.306l.483-.13a.25.25 0 1 1 .13.483l-.483.13a.25.25 0 0 1-.306-.177ZM3.045 12.944a.299.299 0 0 1-.029-.376l3.898-5.592a.25.25 0 0 1 .062-.062l5.602-3.884a.278.278 0 0 1 .392.392L9.086 9.024a.25.25 0 0 1-.062.062l-5.592 3.898a.299.299 0 0 1-.382-.034l-.005-.006Zm3.143 1.817a.25.25 0 0 1-.176-.306l.129-.483a.25.25 0 0 1 .483.13l-.13.483a.25.25 0 0 1-.306.176ZM9.553 2.204a.25.25 0 0 1-.177-.306l.13-.483a.25.25 0 1 1 .483.13l-.13.483a.25.25 0 0 1-.306.176Z" />
                    </svg>
                </a>
            </div>
        </div>
    </div>

    <!-- 下方的左右两栏布局 -->
    <div class="container-fluid">
        <div class="row">

            <!-- 左侧栏: 图片+表格 -->
            <div class="col-12">
                <div class="constainer outside_border" style="margin-right: 0 !important;">
                    <div class="container add_bottom_margin" id="tabs">
                        <!-- bootstrap 导航栏 -->
                        <ul class="nav nav-tabs" id="myTab" role="tablist">
                            <li class="nav-item">
                                <a class="nav-link my_text_font active" id="table-tab" data-toggle="tab" href="#table"
                                    role="tab" aria-controls="table" aria-selected="true">详细信息</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link my_text_font" id="menu-tab" data-toggle="tab" href="#menu" role="tab"
                                    aria-controls="menu" aria-selected="false">目录</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link my_text_font" id="picture-tab" data-toggle="tab" href="#picture"
                                    role="tab" aria-controls="picture" aria-selected="false">购买</a>
                            </li>
                        </ul>
                    </div>
                    <div class="container">
                        <div class="tab-content" id="myTabContent">
                            <div class="tab-pane fade show active" id="table" role="tabpanel"
                                aria-labelledby="table-tab" style="padding-top: 15px; padding-bottom: 15px;">
                                <dl class="row" v-if="book_info && Object.keys(book_info).length > 0">
                                    <template v-for="(value, key) in book_info" :key="key">
                                        <dt class="col-sm-3 text-truncate">{{ key }}</dt>
                                        <dd class="col-sm-9">{{ value }}</dd>
                                    </template>
                                </dl>
                                <p v-else class="text-muted" style="padding-left: 15px; padding-right: 15px;">
                                    暂无详细信息。
                                </p>
                            </div>

                            <div class="tab-pane fade" id="menu" role="tabpanel" aria-labelledby="menu-tab"
                                style="padding-top: 15px; padding-bottom: 15px;">
                                <dl class="row mt-3" v-if="book_menu && book_menu.length > 0">
                                    <dt class="col-sm-3 text-truncate">目录</dt>
                                    <dd class="col-sm-9">
                                        <ul class="list-unstyled mb-0">
                                            <li v-for="(item, index) in book_menu" :key="index">{{ item }}</li>
                                        </ul>
                                    </dd>
                                </dl>
                                <p v-else-if="book_menu && book_menu.length === 0" class="text-muted mt-3"
                                    style="padding-left: 15px; padding-right: 15px;">
                                    暂无目录信息。
                                </p>
                            </div>

                            <div class="tab-pane fade" id="picture" role="tabpanel" aria-labelledby="picture-tab"
                                style="padding-top: 15px; padding-bottom: 15px;">
                                <div v-if="book_shops && book_shops.length > 0">
                                    <div v-for="(shop, index) in book_shops" :key="index" class="card mb-3">
                                        <div class="card-body">
                                            <h5 class="card-title">
                                                <!-- <a :href="shop.link" target="_blank" rel="noopener noreferrer">{{ shop.name }}</a> -->
                                                <p>{{ shop.name }}</p>
                                            </h5>
                                            <p class="card-text">
                                                <strong>价格：</strong> {{ shop.price }}
                                            </p>
                                            <a :href="shop.link" target="_blank" rel="noopener noreferrer"
                                                class="btn btn-primary btn-sm">前往购买</a>
                                        </div>
                                    </div>
                                </div>
                                <p v-else class="text-muted" style="padding-left: 15px; padding-right: 15px;">
                                    暂无购买渠道信息。
                                </p>
                            </div>

                        </div>
                    </div>
                </div>
            </div>

            <!-- 右侧栏: 其他元数据+可视化 -->
            <!-- <div class="col-4">
                <div class="constainer outside_border" style="margin-left: 0 !important;">
                    <h2>Data + Visualization</h2>
                </div>
            </div> -->
        </div>
    </div>
</template>

<script>
import axios from 'axios';
import ClipboardJS from 'clipboard';

export default {
    data() {
        return {
            isLogin: false,

            showAllAuthors: false,

            book_title: "NULL",
            book_author: "NULL",
            book_publisher: "NULL",
            book_publish_year: null,
            book_publish_month: null,
            book_pages: null,
            book_ISBN: "NULL",
            book_price: null,
            book_layout: "NULL",
            book_related_intro: "NULL",
            book_star_rate: [],
            book_total_star_rate: 0.0,
            book_authors: [],
            book_shops: [],
            book_url: "NULL",
            book_douban_id: "NULL",
            book_menu: [],
            book_img_link: "NULL",
            book_tag: "NULL",
            book_info: {},
            person_list: {},

            book_is_starred: false,

            display_summary_window: false,
            model_model_type: "NULL",
            model_message: "NULL",
            last_chat_history: {},
            isPopoverVisible: false,
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
            this.getPaperInfo(); 
            $(function () {
                // $("#tabs").tabs();
            });
            // this.paper_id = this.$route.query.id;
            $(function () {
                $('[data-toggle="popover"]').popover();
                // $('[data-toggle="popover2"]').popover();
            });
        },


        getPaperInfo() {
            const _ID = this.$route.query.id;
            this.paper_id = _ID;
            axios.get('http://10.80.158.19:8088/api/v1/book/info', {
                params: {
                    id: _ID,
                }
            })
                .then((response) => {
                    // 响应数据待处理
                    this.book_title = response.data.title;
                    this.book_author = response.data.author;
                    this.book_publisher = response.data.publisher;
                    this.book_publish_year = response.data.publish_year;
                    this.book_publish_month = response.data.publish_month;
                    this.book_pages = response.data.pages;
                    this.book_ISBN = response.data.ISBN;
                    this.book_price = response.data.price;
                    this.book_layout = response.data.layout;
                    this.book_related_intro = response.data.related_intro;
                    this.book_star_rate = response.data.star_rate;
                    this.book_authors = response.data.authors;
                    this.book_shops = response.data.shops;
                    this.book_url = response.data.url;
                    this.book_douban_id = response.data.douban_id;
                    this.book_menu = response.data.menu;
                    this.book_img_link = response.data.img_link;
                    this.book_tag = response.data.tag;
                    this.book_info = response.data.book_info;
                    this.book_is_starred = response.data.stared;

                    this.book_total_star_rate = this.book_star_rate[0] * 5
                        + this.book_star_rate[1] * 4
                        + this.book_star_rate[2] * 3
                        + this.book_star_rate[3] * 2
                        + this.book_star_rate[4] * 1;


                    response.data.authors.forEach(person => {
                        const role = person["role"];
                        if (role != "作者" && role in this.person_list) {
                            // 如果 role 已存在于 people_list 中，添加到对应的数组
                            this.person_list[role].push(person);
                        } else if (role != "作者") {
                            // 如果 role 不存在，创建一个新键值对
                            this.person_list[role] = [person];
                        }
                    });

                    console.log("Got Book [" + this.paper_id + "] data");
                })
                .catch((error) => {
                    console.log(error);
                    this.paper_id = "ERROR when getting [" + this.paper_id + "] book";
                });

            console.log("hello");
            console.log(this.person_list);
        },

        starBook() {
            axios.get('http://10.80.158.19:8088/api/v1/user/star', {
                params: {
                    id: this.book_douban_id,
                }
            })
                .then((response) => {
                    action = response.data.action;
                    // if (action == "removed") {
                    //     this.book_is_starred = false;
                    // } else if (action == "added") {
                    //     this.book_is_starred = true;
                    // }
                    // 不用返回值来判断是否收藏, 纯前端静态控制
                })
                .catch((error) => {
                    console.log(error);
                });
            this.book_is_starred = !this.book_is_starred;
        },

        SearchAuthor(_name) {
            var _url = "/searchResult?field=author" + "&info=" + encodeURIComponent(_name);
            window.open(_url, "_blank");
        },

        copyLink() {
            const textToCopy = this.book_ISBN;
            const clipboard = new ClipboardJS('.copy-button', {
                text: () => textToCopy
            });

            clipboard.on('success', () => {
                // 只操作当前按钮的 popover
                const popoverElement = $(event.currentTarget);
                popoverElement.popover('show');
                setTimeout(() => {
                    popoverElement.popover('hide');
                }, 1000);
                clipboard.destroy(); // 用完销毁，避免多次绑定
            });

            clipboard.onClick({
                target: document.querySelector('.copy-button')
            });
        },

        togglePopover() {
            this.isPopoverVisible = !this.isPopoverVisible;
        },

        scrollToBottom() {
            const chatContainer = document.querySelector(".chat-container");
            chatContainer.scrollTop = chatContainer.scrollHeight;
        },

        getOriginWebsite() {
            return this.book_url;
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
    },

    watch: {
        // abstractLatex(newValue, oldValue) {
        //     // 每当computedData更新时，这个函数将被调用
        //     this.removeKatexHtmlElements();
        // }
    },


    computed: {
        totalRatingFullStars() {
            // Number of full stars
            return Math.floor(this.book_total_star_rate);
        },
        totalRatingPartialStarVisible() {
            // Check if there's a fractional part for the partial star
            // Using a small epsilon for robust floating point comparison, e.g. 3.0 should not show partial star
            return (this.book_total_star_rate - Math.floor(this.book_total_star_rate)) > 0.001;
        },
        totalRatingPartialStarWidth() {
            // Calculate the width percentage for the partial star
            if (!this.totalRatingPartialStarVisible) return '0%';
            const fraction = this.book_total_star_rate - Math.floor(this.book_total_star_rate);
            return (fraction * 100) + '%';
        },
        totalRatingEmptyStars() {
            // Number of empty stars to complete a total of 5 stars
            // Math.ceil rounds up, so if rating is 3.84, it considers 4 stars (3 full + 1 partial)
            // If rating is 3.0, it considers 3 stars.
            return 5 - Math.ceil(this.book_total_star_rate);
        },
    }
};
</script>


<style>
.set_margin {
    margin-top: 20px;
    margin-right: 20px;
    margin-left: 20px;
}

.set_padding {
    padding-top: 30px !important;
    padding-bottom: 10px !important;
}

html,
body {
    height: 100%;
}

.container,
.row {
    height: 100%;
}

.align-self-center {
    align-self: center;
}

.middle_title {
    text-align: center !important;
}

.no_under_margin {
    margin-bottom: 0;
}


.btn_circle_paper {
    width: 36.781px;
    height: 36.781px;
    border-radius: 10%;
    position: relative;
    padding: 0;
    overflow: visible;
    border: none;
}

.btn_circle_paper :active {
    border: 10px solid white;
}

.btn_circle_paper :active {
    position: absolute;
    top: 50%;
    left: 50%;
}

.inner_btn_check {
    width: 34.781px;
    height: 34.781px;
    position: relative !important;
}

.resize {
    width: 30%;
    height: 150%;
    margin: 0 auto;
    padding-bottom: 150px;
    /* 足够覆盖 footer 的高度 */
}

.button-with-text {
    display: flex;
    align-items: center;
}

.submit_button {
    display: flex;
    justify-content: center;
}

.popover_content {
    background-color: white;
    padding: 20px;
    border-radius: 10px;
    height: 100%;
}


.agree-section {
    margin-top: 20px;
}

/* 弹出框内按钮的容器 */
.popover-buttons {
    margin-left: auto;
    /* 将按钮组推到右侧 */
}


/* .popover-content {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
    } */

/* 按钮容器的样式 */
.buttons-container {
    margin-top: 20px;
    /* 在内容和按钮之间添加一些空间 */
    align-self: flex-end;
    /* 将按钮组推到右侧 */
}

.centered-text {
    line-height: 30px;
    /* 设置行高为与父元素高度相等 */
    height: 30px;
    /* 设置高度为与父元素相等 */
}

.send_btn {
    background-color: #007bff;
    color: white;
    border: none;
    padding: 10px 20px;
    cursor: pointer;
}

.close-btn {
    position: absolute;
    /* 相对于 .fullscreen_popover 定位 */
    top: 15px;
    /* 距离弹窗顶部的距离 */
    right: 15px;
    /* 距离弹窗右侧的距离 */
    padding: 5px 10px;
    /* 按钮内边距，根据需要调整 */
    background: #f5f5f5;
    /* 按钮背景颜色，根据需要调整 */
    border: 1px solid #ddd;
    /* 按钮边框，根据需要调整 */
    cursor: pointer;
    /* 使鼠标悬停时呈现为手型指针 */
    font-size: 15px;
    /* 根据需要调整字体大小 */
    border-radius: 4px;
    /* 如果您希望按钮角是圆的 */
    /* 也可以直接设置宽度和高度 */
    width: 55px;
    /* 根据需要调整宽度 */
    height: 40px;
    /* 根据需要调整高度 */
}

.fullscreen_popover {
    position: fixed;
    /* 固定定位 */
    top: 50%;
    /* 垂直居中 */
    left: 80%;
    /* 水平居中 */
    transform: translate(-50%, -50%);
    /* 调整定位以确保完全居中 */
    width: 400px;
    /* 固定宽度 */
    height: 700px;
    /* 固定高度 */
    background-color: white;
    z-index: 1000;
    box-shadow: 0 0 15px rgba(0, 0, 0, 0.2);
    display: flex;
    flex-direction: column;
}

.popover_content {
    padding: 20px;
    border-radius: 10px;
    display: flex;
    flex-direction: column;
    height: 100%;
}

.chat-container {
    flex-grow: 1;
    /* 使聊天内容区域占据剩余空间 */
    overflow-y: auto;
    /* 仅使聊天内容可滚动 */
    padding: 10px;
}

.chat-content {
    padding: 10px;
    /* 内边距 */
}

.chat-message {
    margin-bottom: 10px;
    /* 信息间距 */
    padding: 5px;
    /* 内边距 */
    border-radius: 5px;
    /* 圆角边框 */
}

.user-message {
    background-color: #e0e0e0;
    /* 用户消息背景颜色 */
    text-align: right;
    /* 用户消息右对齐 */
}

.gpt-message {
    background-color: #f0f0f0;
    /* GPT 消息背景颜色 */
    text-align: left;
    /* GPT 消息左对齐 */
}

.chat-input-container {
    display: flex;
    /* 水平布局 */
    padding: 10px;
    /* 内边距 */
}

.table {
    margin: 20px auto;
    border-collapse: collapse;
    width: 80%;
    background-color: #fff;
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
}

.caption {
    font-size: 24px;
    font-weight: bold;
    text-align: center;
    padding-bottom: 10px;
}

/* 设置奇偶行的背景色 */
.tr:nth-child(odd) {
    background-color: #f2f2f2;
}

/* 设置表格列的边框样式和文本居中 */
.th,
.td {
    border: 1px solid #ccc;
    text-align: center;
    padding: 8px;
}

#chatInput {
    flex-grow: 1;
    /* 输入框占据剩余空间 */
    margin-right: 10px;
    /* 与发送按钮间距 */
}

.reform_table_index {
    margin-left: 10px !important;
    background-color: #4c8dae !important;
}

.reform_badge_outline {
    color: #2578b5;
    background-color: transparent !important;
    border: solid 1px #2578b5 !important;
    border-color: #2578b5 !important;
    padding: 0.1rem 0.1rem !important;
}

.reform_badge_solid {
    color: #ffffff;
    background-color: #2578b5 !important;
    border: solid 1px #2578b5 !important;
    border-color: #2578b5 !important;
    padding: 0.25rem 0.5rem !important;
}

.not {
    display: none;
}

.full_screen {
    width: 100% !important;
}

.my_text_font {
    font-weight: 700 !important;
    color: #2578b5 !important;
}

.outside_border {
    border: 10px solid #dee2e6 !important;
    border-radius: 1rem;
    margin-top: 20px !important;
    margin-right: 20px;
    margin-left: 20px;
    margin-bottom: 50px !important;
    padding: 20px !important;
}

.add_bottom_margin {
    margin-bottom: 20px;
}

.pic_gap {
    border-color: #643441;
    background-color: #643441;
    margin-top: 16px !important;
    margin-bottom: 16px !important;
    padding-top: 3px !important;
    padding-bottom: 3px !important;
}
</style>