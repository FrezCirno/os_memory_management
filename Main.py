import sys
import random
from PyQt5 import QtCore, QtGui, QtWidgets
from gui import Ui_QWidget


def SKIP():
    m = random.randint(0, 159)
    while True:
        yield m  # down [0,159]
        m += 1
        yield m  # next [1,160]
        m = random.randint(161, 318)
        yield m  # up [161,318]
        m += 1
        yield m  # next [162,319]
        m = random.randint(0, 159)


def SEQU():
    count = 0
    while True:
        yield count
        count += 1
        if count >= 320:
            count = 0


def RAND():
    while True:
        yield random.randint(0, 319)


class MainForm(QtWidgets.QWidget):
    def __init__(self):
        super(MainForm, self).__init__()
        self.ui = Ui_QWidget()
        self.ui.setupUi(self)

        self.count = 0
        self.clock = 0
        self.page_fault = 0
        self.sequence = SKIP()
        self.swap_policy = self.FIFO
        self.page_bars = (self.ui.page_1, self.ui.page_2, self.ui.page_3, self.ui.page_4)
        self.page_labels = (self.ui.page_label_1, self.ui.page_label_2, self.ui.page_label_3, self.ui.page_label_4)
        self.page_nums = [-1, -1, -1, -1]
        self.fresh_time = [-1, -1, -1, -1]
        self.access_time = [-1, -1, -1, -1]
        self.page_bar_pos = [page.pos() for page in self.page_bars]
        self.animation_bars = (self.ui.temp_1, self.ui.temp_2, self.ui.temp_3, self.ui.temp_4)

        self.table = self.ui.table
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['地址', '所在页', '缺页', '换出页', '换入页'])
        self.table.setColumnWidth(0, 60)
        self.table.setColumnWidth(1, 90)
        self.table.setColumnWidth(2, 60)
        self.table.setColumnWidth(3, 90)
        self.table.setColumnWidth(4, 90)

        self.consecu_timer = QtCore.QTimer()
        self.consecu_timer.timeout.connect(self.ui.single_step.click)

        self.ui.reset_all.click()
        self.show()

        # self.ui.widget.highlight = 1

    @QtCore.pyqtSlot(int)
    def on_algo_currentIndexChanged(self, index):
        self.swap_policy = self.FIFO if self.ui.algo.currentText() == 'FIFO' else self.LRU

    @QtCore.pyqtSlot(int)
    def on_sequence_currentIndexChanged(self, index):
        text = self.ui.sequence.currentText()
        if text == 'SKIP':
            self.sequence = SKIP()
        elif text == '顺序':
            self.sequence = SEQU()
        else:
            self.sequence = RAND()

    @QtCore.pyqtSlot()
    def on_reset_all_clicked(self):
        if self.ui.consecu_step.isChecked():
            self.ui.consecu_step.click()

        for index in range(len(self.page_labels)):
            self.page_labels[index].setHidden(True)
            self.page_bars[index].setHidden(True)
            self.animation_bars[index].setHidden(True)
            self.page_nums[index] = -1
            self.fresh_time[index] = -1
            self.access_time[index] = -1
        self.count = 0
        self.clock = 0
        self.page_fault = 0
        self.ui.pf_count.setHidden(True)
        self.ui.pf_rate.setHidden(True)
        self.table.setRowCount(0)

    @QtCore.pyqtSlot()
    def on_consecu_step_clicked(self):
        if self.ui.consecu_step.isChecked():
            self.consecu_timer.start(20)
        else:
            self.consecu_timer.stop()

    @QtCore.pyqtSlot()
    def on_single_step_clicked(self):
        if self.count >= 320:
            if self.ui.consecu_step.isChecked():
                self.ui.consecu_step.click()
            self.ui.pf_count.setText("缺页次数: %d" % self.page_fault)
            self.ui.pf_count.setVisible(True)
            self.ui.pf_rate.setText("缺页率: %.2f%%" % (100 * self.page_fault / self.count))
            self.ui.pf_rate.setVisible(True)
            return

        index = next(self.sequence)
        page = index // 10
        in_index = index % 10
        self.table.insertRow(self.count)
        self.table.setItem(self.count, 0, QtWidgets.QTableWidgetItem(str(index)))
        self.table.setItem(self.count, 1, QtWidgets.QTableWidgetItem(str(page)))

        for index in range(len(self.page_nums)):
            if self.page_nums[index] == page:  # 命中
                target = index
                self.access_time[index] = self.clock
                self.table.setItem(self.count, 2, QtWidgets.QTableWidgetItem('否'))
                self.table.setItem(self.count, 3, QtWidgets.QTableWidgetItem('-'))
                self.table.setItem(self.count, 4, QtWidgets.QTableWidgetItem('-'))
                break
        else:  # 不命中
            self.page_fault += 1
            target = self.swap_policy(page)  # 换页
            old_page = self.page_nums[target]
            self.swap(target, page)
            self.table.setItem(self.count, 2, QtWidgets.QTableWidgetItem('是'))
            self.table.setItem(self.count, 3,
                               QtWidgets.QTableWidgetItem(str(old_page) if old_page != -1 else '-'))
            self.table.setItem(self.count, 4, QtWidgets.QTableWidgetItem(str(page)))

        self.page_bars[target].highlight = in_index
        animation = QtCore.QPropertyAnimation(self.page_bars[target], b'color', self)
        animation.setDuration(500)
        animation.setStartValue(QtGui.QColor(255, 0, 0))
        animation.setEndValue(QtGui.QColor(0, 255, 0))
        animation.start()

        self.table.selectRow(self.count)
        self.count += 1
        self.clock += 1

    def swap(self, replaced: int, new_page):
        return_value = self.page_nums[replaced]
        self.fresh_time[replaced] = self.clock
        self.access_time[replaced] = self.clock
        self.page_nums[replaced] = new_page

        page_bar: QtWidgets.QProgressBar = self.page_bars[replaced]
        page_bar_pos = self.page_bar_pos[replaced]
        temp_bar: QtWidgets.QProgressBar = self.animation_bars[replaced]

        self.page_labels[replaced].setText("PAGE %d" % new_page)
        self.page_labels[replaced].setVisible(True)

        animation1 = QtCore.QPropertyAnimation(page_bar, b"pos")
        animation1.setDuration(200)
        animation1.setStartValue(
            QtCore.QPoint(self.page_bar_pos[replaced].x(), self.page_bar_pos[replaced].y() - page_bar.height()))
        animation1.setEndValue(page_bar_pos)

        animation2 = QtCore.QPropertyAnimation(temp_bar, b'pos')
        animation2.setDuration(200)
        animation2.setStartValue(page_bar_pos)
        animation2.setEndValue(
            QtCore.QPoint(self.page_bar_pos[replaced].x(), self.page_bar_pos[replaced].y() + page_bar.height()))

        temp_bar_opacity = QtWidgets.QGraphicsOpacityEffect(self)
        temp_bar.setGraphicsEffect(temp_bar_opacity)
        animation3 = QtCore.QPropertyAnimation(temp_bar_opacity, b'opacity')
        animation3.setDuration(200)
        animation3.setStartValue(1.0)
        animation3.setEndValue(0.0)

        old_bar_opacity = QtWidgets.QGraphicsOpacityEffect(self)
        page_bar.setGraphicsEffect(old_bar_opacity)
        animation4 = QtCore.QPropertyAnimation(old_bar_opacity, b'opacity')
        animation4.setDuration(200)
        animation4.setStartValue(0.0)
        animation4.setEndValue(1.0)

        ag = QtCore.QParallelAnimationGroup(self)
        ag.addAnimation(animation1)
        ag.addAnimation(animation4)
        if page_bar.isVisible():
            temp_bar.show()
            ag.addAnimation(animation2)
            ag.addAnimation(animation3)
            ag.finished.connect(lambda x=temp_bar: x.hide())
        else:
            page_bar.setVisible(True)
        ag.start()

        return return_value

    def FIFO(self, new_page):
        replaced = 0
        for i, fresh_time in enumerate(self.fresh_time):
            if fresh_time < self.fresh_time[replaced]:
                replaced = i
        return replaced

    def LRU(self, new_page):
        replaced = 0
        for i, access_time in enumerate(self.access_time):
            if access_time < self.access_time[replaced]:
                replaced = i
        return replaced


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    form = MainForm()
    sys.exit(app.exec())
