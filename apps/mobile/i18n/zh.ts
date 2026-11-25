import type { Translation } from './en';

const zh: Translation = {
  tabs: {
    home: '首页',
    research: '研究',
    ai: 'AI',
    portfolio: '持仓',
  },
  settings: {
    title: '设置',
    language: '语言',
  },
  watchlist: {
    empty: '暂无自选股',
    search: '搜索',
    add: '加入自选',
    remove: '移出自选',
  },
  search: {
    placeholder: '搜索',
    noResults: '无结果',
    etf: 'ETF',
  },
  market: {
    dailyClose: '每日收盘 · {{date}} · {{source}}',
    noPrices: '暂无价格数据',
    ranges: {
      '1M': '1月',
      '3M': '3月',
      '6M': '6月',
      '1Y': '1年',
      '5Y': '5年',
    },
  },
  errors: {
    serverUnreachable: '无法连接服务器',
    symbolNotFound: '未找到该代码',
    dataUnavailable: '行情数据暂不可用',
    quotaExceeded: '已达数据额度上限，请稍后再试',
    generic: '出现错误',
    retry: '重试',
  },
};

export default zh;
