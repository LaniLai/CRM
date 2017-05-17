# ！/usr/bin/env python
# -*- coding:utf-8 -*-
# __Author__ Jianer


class Pagination(object):
    def __init__(self, totalCount, currentPage, perPageItemNum=5, maxPageNum=9):
        """
        :param totalCount:     所有数据总个数
        :param currentPage:    当前页码
        :param perPageItemNum: 每页显示行数
        :param maxPageNum:     最多显示页码个数
        """
        self.total_count = totalCount
        # 对当前的页码进行一次异常捕获
        try:
            currentPage = int(currentPage)
            if currentPage <= 0:
                currentPage = 1
            self.current_page = currentPage
        except Exception:
            self.current_page = 1
        self.per_page_item_num = perPageItemNum
        self.max_page_num = maxPageNum

    @property
    def start(self):
        return (self.current_page - 1) * self.per_page_item_num

    @property
    def end(self):
        return self.current_page * self.per_page_item_num

    @property
    def num_pages(self):
        """
        总页数
        :return:
        """
        # 得商取余得内置函数
        x, o = divmod(self.total_count, self.per_page_item_num)
        if o == 0:
            return x
        return x + 1

    @property
    def page_num_range(self):
        if self.num_pages < self.max_page_num:
            return range(1, self.num_pages + 1)

        part = self.max_page_num // 2
        if self.current_page <= part:
            return range(1, self.max_page_num + 1)

        if (self.current_page + part) > self.num_pages:
            return range(self.num_pages - self.max_page_num + 1, self.num_pages + 1)
        return range(self.current_page - part, self.current_page + part + 1)

    def page_str(self, current_url):
        if '?' not in current_url:
            current_url += '?'
        import re
        ret = re.search("&?pager=\d+$", current_url)
        if ret:
            current_url = current_url.strip(ret.group())
        page_list = []
        # print(current_url)
        first = "<li><a href='%s&pager=1'>首页</a></li>" % (current_url)
        page_list.append(first)

        if self.current_page == 1:
            prev_page = "<li class='disabled'><a>上一页</a></li>"
        else:
            prev_page = "<li><a href='%s&pager=%s'>上一页</a></li>" % (current_url, self.current_page - 1)
        page_list.append(prev_page)

        for i in self.page_num_range:
            if i == self.current_page:
                temp = "<li class='active'><a href='%s&pager=%s'>%s</a></li>" % (current_url, i, i)
            else:
                temp = "<li><a href='%s&pager=%s'>%s</a></li>" % (current_url, i, i)
            page_list.append(temp)

        if self.current_page == self.num_pages:
            next_page = "<li class='disabled'><a>下一页</a></li>"
        else:
            next_page = "<li><a href='%s&pager=%s'>下一页</a></li>" % (current_url, self.current_page + 1)
        page_list.append(next_page)

        last = "<li><a href='{0}&pager={1}'>尾页</a></li>".format(current_url, self.num_pages)
        page_list.append(last)
        outline = "<li class='disabled'><a href='javascript:void(0)' >共 %d页 / %d 条数据</a></li>"\
                  %(self.num_pages, self.total_count)
        page_list.append(outline)
        return ''.join(page_list)
