"use strict";
var __create = Object.create;
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __getProtoOf = Object.getPrototypeOf;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toESM = (mod, isNodeMode, target) => (target = mod != null ? __create(__getProtoOf(mod)) : {}, __copyProps(
  // If the importer is in node compatibility mode or this is not an ESM
  // file that has been converted to a CommonJS file using a Babel-
  // compatible transform (i.e. "__esModule" has not been set), then set
  // "default" to the CommonJS "module.exports" for node compatibility.
  isNodeMode || !mod || !mod.__esModule ? __defProp(target, "default", { value: mod, enumerable: true }) : target,
  mod
));
var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

// scripts/fetch-tweets.ts
var fetch_tweets_exports = {};
__export(fetch_tweets_exports, {
  fetchTweets: () => fetchTweets
});
module.exports = __toCommonJS(fetch_tweets_exports);

// scripts/utils.ts
var import_twitter_openapi_typescript = require("twitter-openapi-typescript");
var import_axios = __toESM(require("axios"), 1);
var import_twitter_api_v2 = require("twitter-api-v2");
var import_fs = __toESM(require("fs"), 1);

// config.json
var config_default = {
  AUTH_TOKEN: "",
  GET_ID_X_TOKEN: "",
  PROXY_URL: "",
  logging: {
    enableConsoleLog: true,
    enableFileLog: true
  }
};

// scripts/utils.ts
var PROXY_URL = config_default.PROXY_URL;
var getProxiedUrl = (url) => {
  if (url.startsWith(PROXY_URL)) {
    return url;
  }
  return PROXY_URL ? `${PROXY_URL}${url}` : url;
};
var originalFetchApi = import_twitter_openapi_typescript.TwitterOpenApi.fetchApi;
import_twitter_openapi_typescript.TwitterOpenApi.fetchApi = async (url, init) => {
  const proxiedUrl = getProxiedUrl(url);
  console.log(`\u4EE3\u7406\u8BF7\u6C42: ${url} -> ${proxiedUrl}`);
  return originalFetchApi(proxiedUrl, init);
};
var _xClient = async (TOKEN) => {
  console.log("\u{1F680} ~ const_xClient= ~ TOKEN:", TOKEN.slice(0, 3) + "***");
  try {
    const response = await import_axios.default.get(getProxiedUrl("https://x.com/manifest.json"), {
      headers: {
        cookie: `auth_token=${TOKEN}`
      },
      timeout: 1e4
    });
    if (response.status !== 200) {
      throw new Error(`HTTP\u9519\u8BEF! \u72B6\u6001: ${response.status}`);
    }
    console.log("\u8BF7\u6C42\u6210\u529F\uFF0C\u89E3\u6790cookie");
    const cookies = response.headers["set-cookie"] || [];
    console.log("cookies", cookies);
    const cookieObj = cookies.reduce((acc, cookie) => {
      const [name, value] = cookie.split(";")[0].split("=");
      acc[name] = value;
      return acc;
    }, {});
    console.log("\u521D\u59CB\u5316TwitterOpenApi");
    const api = new import_twitter_openapi_typescript.TwitterOpenApi();
    const client = await api.getClientFromCookies({ ...cookieObj, auth_token: TOKEN });
    console.log("\u5DF2\u521B\u5EFA\u5BA2\u6237\u7AEF\uFF0C\u4F46X API\u8BF7\u6C42\u9700\u8981\u624B\u52A8\u6DFB\u52A0\u4EE3\u7406\u524D\u7F00");
    console.log("Twitter URL: https://api.twitter.com -> \u4EE3\u7406URL: " + getProxiedUrl("https://api.twitter.com"));
    return client;
  } catch (error) {
    console.error("\u8BF7\u6C42x.com\u5931\u8D25:", error.message);
    import_fs.default.writeFileSync("error.log", JSON.stringify({
      message: error.message,
      stack: error.stack
    }, null, 2));
    throw error;
  }
};
var XAuthClient = () => _xClient(config_default.AUTH_TOKEN);

// scripts/fetch-tweets.ts
var import_lodash = require("lodash");
var import_dayjs = __toESM(require("dayjs"), 1);
var import_fs_extra = __toESM(require("fs-extra"), 1);
var fetchTweets = async () => {
  const client = await XAuthClient();
  const resp = await client.getTweetApi().getHomeLatestTimeline({
    count: 100
  });
  const originalTweets = resp.data.data.filter((tweet) => {
    return !tweet.referenced_tweets || tweet.referenced_tweets.length === 0;
  });
  const rows = [];
  originalTweets.forEach((tweet) => {
    const isQuoteStatus = (0, import_lodash.get)(tweet, "raw.result.legacy.isQuoteStatus");
    if (isQuoteStatus) {
      return;
    }
    const fullText = (0, import_lodash.get)(tweet, "raw.result.legacy.fullText", "RT @");
    if (fullText?.includes("RT @")) {
      return;
    }
    const createdAt = (0, import_lodash.get)(tweet, "raw.result.legacy.createdAt");
    if ((0, import_dayjs.default)().diff((0, import_dayjs.default)(createdAt), "day") > 1) {
      return;
    }
    const screenName = (0, import_lodash.get)(tweet, "user.legacy.screenName");
    const tweetUrl = `https://x.com/${screenName}/status/${(0, import_lodash.get)(
      tweet,
      "raw.result.legacy.idStr"
    )}`;
    const user = {
      screenName: (0, import_lodash.get)(tweet, "user.legacy.screenName"),
      name: (0, import_lodash.get)(tweet, "user.legacy.name"),
      profileImageUrl: (0, import_lodash.get)(tweet, "user.legacy.profileImageUrlHttps"),
      description: (0, import_lodash.get)(tweet, "user.legacy.description"),
      followersCount: (0, import_lodash.get)(tweet, "user.legacy.followersCount"),
      friendsCount: (0, import_lodash.get)(tweet, "user.legacy.friendsCount"),
      location: (0, import_lodash.get)(tweet, "user.legacy.location")
    };
    const mediaItems = (0, import_lodash.get)(
      tweet,
      "raw.result.legacy.extendedEntities.media",
      []
    );
    const images = mediaItems.filter((media) => media.type === "photo").map((media) => media.mediaUrlHttps);
    const videos = mediaItems.filter(
      (media) => media.type === "video" || media.type === "animated_gif"
    ).map((media) => {
      const variants = (0, import_lodash.get)(media, "videoInfo.variants", []);
      const bestQuality = variants.filter((v) => v.contentType === "video/mp4").sort((a, b) => (b.bitrate || 0) - (a.bitrate || 0))[0];
      return bestQuality?.url;
    }).filter(Boolean);
    rows.push({
      // @ts-ignore
      user,
      images,
      videos,
      tweetUrl,
      fullText
    });
  });
  const outputPath = `./tweets/${(0, import_dayjs.default)().format("YYYY-MM-DD")}.json`;
  let existingRows = [];
  if (import_fs_extra.default.existsSync(outputPath)) {
    existingRows = JSON.parse(import_fs_extra.default.readFileSync(outputPath, "utf-8"));
  }
  const allRows = [...existingRows, ...rows];
  const uniqueRows = Array.from(
    new Map(allRows.map((row) => [row.tweetUrl, row])).values()
  );
  const sortedRows = uniqueRows.sort((a, b) => {
    const urlA = new URL(a.tweetUrl);
    const urlB = new URL(b.tweetUrl);
    const idA = urlA.pathname.split("/").pop() || "";
    const idB = urlB.pathname.split("/").pop() || "";
    return idB.localeCompare(idA);
  });
  console.log(sortedRows);
  return sortedRows;
};
fetchTweets();
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  fetchTweets
});
//# sourceMappingURL=fetch-tweets.cjs.map