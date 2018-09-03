__author__ = 'Administrator'
from django.utils.safestring import mark_safe


class Pagination(object):
    def __init__(self, current_page, data_count, per_page_count=10, pager_num=7):
        try:
            self.current_page = int(current_page)
        except Exception as e:
            self.current_page = 1
        self.data_count = data_count
        self.per_page_count = per_page_count
        self.pager_num = pager_num

    @property
    def start(self):
        return (self.current_page - 1) * self.per_page_count

    @property
    def end(self):
        return self.current_page * self.per_page_count

    @property
    def total_count(self):
        # 計一共有多少頁
        v, y = divmod(self.data_count, self.per_page_count)
        if y:
            v += 1
        return v

    def page_str(self, base_url):
        page_list = []

        if self.total_count < self.pager_num:  # 如果總頁數少於原訂一頁顯示的頁數
            start_index = 1
            end_index = self.total_count + 1  # 一次拿出所有數據
        else:
            if self.current_page <= (self.pager_num + 1) / 2:
                start_index = 1
                end_index = self.pager_num + 1  # 現在頁數於顯示頁數之前
            else:
                start_index = self.current_page - (self.pager_num - 1) / 2  # 將現在的頁數放在中間
                end_index = self.current_page + (self.pager_num + 1) / 2  # 將現在的頁數放在中間
                if (self.current_page + (self.pager_num - 1) / 2) > self.total_count:  # 如果現在頁數+之後顯示的頁數大於總頁數
                    end_index = self.total_count + 1
                    start_index = self.total_count - self.pager_num + 1

        if self.current_page == 1:
            prev = '<li><a class="page" href="javascript:void(0);">上一页</a></li>'
        else:
            prev = '<li><a class="page" href="%s?p=%s">上一页</a></li>' % (base_url, self.current_page - 1,)
        page_list.append(prev)

        for i in range(int(start_index), int(end_index)):
            if i == self.current_page:
                temp = '<li class="active"><a class="page active" href="%s?p=%s">%s</a></li>' % (base_url, i, i)
            else:
                temp = '<li><a class="page" href="%s?p=%s">%s</a></li>' % (base_url, i, i)
            page_list.append(temp)

        if self.current_page == self.total_count:
            nex = '<li><a class="page" href="javascript:void(0);">下一页</a></li>'
        else:
            nex = '<li><a class="page" href="%s?p=%s">下一页</a></li>' % (base_url, self.current_page + 1,)
        page_list.append(nex)

        # jump = """
        # <input type='text'  /><a onclick='jumpTo(this, "%s?p=");'>GO</a>
        # <script>
        #     function jumpTo(ths,base){
        #         var val = ths.previousSibling.value;
        #         location.href = base + val;
        #     }
        # </script>
        # """ % (base_url,)
        #
        # page_list.append(jump)

        page_str = mark_safe("".join(page_list))

        return page_str
