# tv lg channels list updater

import os
import sys
import xml.etree.ElementTree as etree


def print_progs(fn, progs):
    """
    print channels list
    """
    ss = []
    keys = [int(i) for i in progs.keys()]
    pr_nums = [str(i) for i in sorted(keys)]
    for p in pr_nums:
        n = progs[p]["vchName"]
        s = progs[p]["isSkipped"]
        ss.append(f"{n:25s} | {p:5s} | {s:1s}")
    with open(fn, "wt") as f:
        f.write("\n".join(ss))
        f.close()


def get_skip_list(fn):
    """
    channels skip list loader
    """
    print(f"Reading skip list {fn}")
    ss = []
    for line in open(fn, "rt"):
        s = [i.strip() for i in line.split("|")]
        if len(s) == 3:
            if s[2] == "1":  # если признак пропуска, то
                ss.append(s[1])  # название в список
    print(f"Skipped channels {len(ss)}")
    return ss


def set_skip_marks(progs, skip_list):
    """
    transfer user skip list to channels list
    """


def get_progs(fn):
    """
    tv xml loader - prNum, vchName, isSkipped
    """
    print(f"Reading cnahhels list {fn}")
    tree = etree.parse(fn)
    root = tree.getroot()
    channels = root.find('CHANNEL')
    dtv = channels.find('DTV')
    progs_skipped = []
    progs_all = {}
    skipped = 0
    for i in dtv:
        p = i.find('prNum').text
        n = i.find('vchName').text
        s = i.find('isSkipped').text
        progs_all[p] = {"prNum": p, "vchName": n, "isSkipped": s}
        # можно проверять потом по имени, но выяснилось, что имена меняются "TV1000" -> "TV 1000"
        # а номер вроде бы пока остается
        # составляем список тех каналов, которые с признаком пропуска isSkipped
        if s == '1':
            progs_skipped.append(p)
            skipped = skipped+1
    print("Skipped channels ", skipped, '/', len(dtv))
    return progs_all, progs_skipped


def set_progs(fn, all_list, progs_to_skip, extra_skip_list):
    """
    transfer skip marks to new channels list
    """
    # fn - новый файл из тв после обновления и поиска новых каналов
    # progs_to_skip - список из старого файла с пропущенными каналами
    # там могут быть другие номера и названия
    # пока ищу по номеру канала (кнопки)
    print(f"Reading new channels list {fn}")
    tree = etree.parse(fn)
    root = tree.getroot()
    channels = root.find('CHANNEL')
    dtv = channels.find('DTV')
    for i in dtv:
        p = i.find('prNum').text
        n = i.find('vchName').text
        s = i.find('isSkipped')

        # печать каналов с одни номером, но разными именами
        if p in all_list:
            if n != all_list[p]["vchName"]:
                print('!!! Warning! Pr %s different names "%s" -> "%s"' %
                      (p, all_list[p]["vchName"], n))

        # если канал есть в списке пропущенных
        s.text = "1" if (p in progs_to_skip) or (p in extra_skip_list) else "0"

    return tree


def save_progs(fn, tree):
    """
    store progs to xml for tv
    """
    print(f"Writing new list to {fn}")
    tree.write(open(fn, 'wb'), encoding='utf-8', xml_declaration=True)


# загружаем список 1
# если рядом нет файла progs_selected_1.txt, то его создаем и заканчиваем
# если рядом есть progs_selected_1.txt, то читаем его, блокируем выбранные каналы
# загружаем список 2
# выключаем каналы и списка заблокированных

# загружаем список, который был ранее
pr_old, pr_skipped = get_progs('1\\GlobalClone00001.TLL')
# если рядом нет списка заблокированных каналов, то создаем его
fn_selected = "1\\progs_selected_1.txt"
if not os.path.exists(fn_selected):
    print(f"Creating blank channels skip list {fn_selected}")
    print_progs(fn_selected, pr_old)
    sys.exit(1)

skip_list = get_skip_list(fn_selected)

# pr_skipped - каналы отмечены в xml аттрибутом isSkipped
# skip_list - каналы в текстовом файле с пометкой 0/1

# новый из телевизора после полного поиска
ps = set_progs('2\\GlobalClone00001.TLL', pr_old, pr_skipped, skip_list)

# результат в файл
save_progs('3\\GlobalClone00001.TLL', ps)

pr_tmp, pr_tmp_skipped = get_progs('2\\GlobalClone00001.TLL')
print_progs("2\\progs_selected_2.txt", pr_tmp)

pr_tmp, pr_tmp_skipped = get_progs('3\\GlobalClone00001.TLL')
print_progs("3\\progs_selected_3.txt", pr_tmp)
