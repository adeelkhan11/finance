import datetime
import re
import math


class TextReport:
    BAR_SYMBOL = '$'
    BAR_WIDTH = 10

    def __init__(self, db, month):
        self.total_overlimit = 0.0
        self.db = db
        self.month = month
        self.head_names = db.loadDicts('head', ['head'], ['name'])

#    def has_opposite_sign(self, num1, num2):
#        return (num1 < 0 and num2 > 0) or (num1 > 0 and num2 < 0)

    def _percentage_bar(self, used, accum_alloc, alloc, head):
        """Return a progress bar to represent allocation usage.

        Keyword Arguments
        used -- The amount used (is positive if used)
        accum_alloc -- Denominator. The amount allocated (also positive). The allowable ceiling,
                       aim to keep amount used below this amount.
        head -- The allocation bucket identifier
        """

        if used <= 0:
            amount = 0
        elif accum_alloc <= 0:
            amount = 9999
        else:
            amount = used / accum_alloc
        bricks = int(round(amount * self.BAR_WIDTH))
        over_indicator = int(bricks / (self.BAR_WIDTH * 3))
        if bricks > self.BAR_WIDTH * 3:
            bricks = self.BAR_WIDTH * 3

        overlimit = ''
        if used > max(accum_alloc, alloc):
            if len(head) > 1:
                x_over = used - max(accum_alloc, alloc)
                overlimit = '{:8,.0f}'.format(x_over)
                if accum_alloc != 0 or alloc != 0:
                    self.total_overlimit += x_over

        return "%s / %s  %s  |%s%s|%-20s%-3s  %s" % (
            '{:8,.0f}'.format(used), '{:8,.0f}'.format(accum_alloc), '{:8,.0f}'.format(alloc),
            self.BAR_SYMBOL * min(bricks, 10),
            '-' * (self.BAR_WIDTH - bricks), self.BAR_SYMBOL * (bricks - 10),
            '>' * min(over_indicator, 3),
            overlimit)

    def show_details(self, head):
        sql = """select tran_date || '-' || sequence, sequence, tran_date, description
            , amount, bank, ifnull(head, '92'), source, notes
            from tran
            where tran_date like ?
            and account not in ('Business', 'Home Loan', 'Vertigo', 'Loan', '037179432768')
            and ifnull(head, '92') = ?
            order by tran_date"""
        details = self.db.loadDictsFromQuery(['date_sequence'],
                                             ['sequence',
                                              'tran_date',
                                              'description',
                                              'amount',
                                              'bank',
                                              'head',
                                              'source',
                                              'notes'],
                                             sql,
                                             [self.month + '%', head])
        print()
        running_bal = 0
        for key in sorted(details.keys()):
            tran = details[key]
            running_bal += tran['amount']
            print("%5d  %10s  %-50s %s %s" % (tran['sequence'],
                                              tran['tran_date'],
                                              re.sub('\s+', ' ',
                                                     ':'.join([self.db.nullToEmpty(tran[k])
                                                               for k in ['description',
                                                                         'source',
                                                                         'notes']]))[:50],
                                              '{:8,.0f}'.format(tran['amount']),
                                              '{:8,.0f}'.format(running_bal)))
        if len(details) > 0:
            print()

    def show_allocations(self, allocations):
        for key in sorted(allocations.keys()):
            alloc = allocations[key]
            if len(alloc['head']) == 1:
                print("=" * 100)
            used = float(alloc['used'])
            allocated = float(alloc['new_alloc'] + alloc['rollover'] + alloc['adjustment'])
            print("%2s %17s: %s" % (alloc['head'],
                                    self.head_names[alloc['head']]['name'],
                                    self._percentage_bar(-used,
                                                         allocated,
                                                         float(alloc['new_alloc']),
                                                         alloc['head'])))
            if len(alloc['head']) == 2:
                self.show_details(alloc['head'])

        print()
        if self.total_overlimit > 0.0:
            print("Over limit by $%s." % '{:,.0f}'.format(self.total_overlimit))
        else:
            print("You are within budget.")

    def show_exceptions(self, allocations):
        total_overlimit = 0
        output = []
        for key in sorted(allocations.keys()):
            head, new_alloc, rollover, adjustment, used = [allocations[key][x] for x in
                                                           ['head', 'new_alloc', 'rollover', 'adjustment', 'used']]
            used = -used
            accum_alloc = float(new_alloc + rollover + adjustment)
            if used > max(accum_alloc, new_alloc):
                if len(head) > 1:
                    x_over = used - max(accum_alloc, new_alloc)
                    if accum_alloc != 0 or new_alloc != 0:
                        output.append("%2s  %-20s %s" % (head, self.head_names[head]['name'][:20],
                                                         '{:8,.0f}'.format(x_over)))
                        total_overlimit += x_over

        if len(output) == 0:
            print("You are within budget.")
        else:
            output.append("%2s  %-20s %s" % ('', 'TOTAL', '{:8,.0f}'.format(total_overlimit)))
            print('-' * 33)
            for l in output:
                print(l)

    def show_header(self):
        width = 100
        gap = 3
        current_month_display = datetime.datetime.strptime(self.month + '-01', "%Y-%m-%d").strftime('%B %Y')
        text_width = len(current_month_display)
        left_side = int((width - text_width) / 2 - gap)
        right_side = int(width - left_side - text_width - (gap * 2))
        result = []
        for i in range(1, 10):
            lw = min(int(math.sin((math.pi / 20) * i) * width), width)
            result.append(' ' * int((width - lw) / 2) + '#' * lw)
        result.append('#' * width)
        result.append('#' * width)
        result.append('#' * left_side + ' ' * (text_width + (gap * 2)) + '#' * right_side)
        result.append('#' * left_side + ' ' * gap + current_month_display + ' ' * gap + '#' * right_side)
        result.append('#' * left_side + ' ' * (text_width + (gap * 2)) + '#' * right_side)
        result.append('#' * width)
        result.append('#' * width)
        print("\n".join(result))
