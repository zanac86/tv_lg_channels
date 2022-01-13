import xml.etree.ElementTree as etree


def print_progs(fn, progs):
    ss = []
    keys = [int(i) for i in progs.keys()]
    pr_nums = [str(i) for i in sorted(keys)]
    for p in pr_nums:
        n = progs[p]["vchName"]
        s = progs[p]["isSkipped"]
        ss.append("%25s %5s %1s" % (n, p, s))
    with open(fn, "wt") as f:
        f.write("\n".join(ss))
        f.close()


def get_progs(fn):
    print(f"Reading skip list {fn}")
    tree = etree.parse(fn)
    root = tree.getroot()
    channels = root.find('CHANNEL')
    dtv = channels.find('DTV')
    progs_skipped = {}
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
            progs_skipped[p] = n
            skipped = skipped+1
    print("Skipped channels ", skipped, '/', len(dtv))
    return progs_all, progs_skipped


def set_progs(fn, all_list, progs_to_skip):
    # fn - новый файл из тв после обновления и поиска новых каналов
    # progs_to_skip - список из старого файла с пропущенными каналами
    # там могут быть другие номера и названия
    # пока ищу по номеру канала (кнопки)
    print(f"Reading full list {fn}")
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
        s.text = "1" if p in progs_to_skip else "0"

    return tree


def save_progs(fn, tree):
    print(f"Writing new list to {fn}")
    tree.write(open(fn, 'wb'), encoding='utf-8', xml_declaration=True)


# старый файл с каналами у которых есть признак пропуска
pr_all, pr_skipped = get_progs('1\\GlobalClone00001.TLL')
# новый из телевизора после полного поиска
ps = set_progs('2\\GlobalClone00001.TLL', pr_all, pr_skipped)
# результата
save_progs('3\\GlobalClone00001.TLL', ps)
print_progs("progs_selected_old.txt", pr_all)

pr_all_new, pr_skipped_new = get_progs('3\\GlobalClone00001.TLL')
print_progs("progs_selected_new.txt", pr_all_new)
