# Whisper Model Performance comparison

## Evaluation machine specs

```bash
quakumei@box:/mnt/nvme-1tb-samsung-evo/projects/current/spbstu/lazy-lecture$ neofetch --off
quakumei@box
------------
OS: Ubuntu 22.04.5 LTS x86_64
Kernel: 6.8.0-47-generic
Uptime: 3 hours, 16 mins
Packages: 2577 (dpkg), 7 (flatpak), 21 (snap)
Shell: bash 5.1.16
Resolution: 1920x1080
DE: Unity
WM: Mutter
WM Theme: Adwaita
Theme: Yaru-sage-dark [GTK2/3]
Icons: Yaru-sage [GTK2/3]
Terminal: vscode
CPU: Intel Xeon E5-2666 v3 (20) @ 3.500GHz
GPU: NVIDIA GeForce RTX 3090
Memory: 8521MiB / 64140MiB
```

Запуск производился в контейнере, без поддержки GPU. При этом, использование CPU ограничивалось 50%.

`sample_ru_120s.mp3` - файл с чтением текста со страницы википедии об [Аналитической геометрии](https://ru.wikipedia.org/wiki/%D0%90%D0%BD%D0%B0%D0%BB%D0%B8%D1%82%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B0%D1%8F_%D0%B3%D0%B5%D0%BE%D0%BC%D0%B5%D1%82%D1%80%D0%B8%D1%8F) в 2 минуты длиной.


## Eval Results

Ниже представлены результаты тестов запуска команды `time whisper sample_ru_120s.mp3 --model <MODEL> --language ru --model_dir /cache --device cpu` по времени исполнения.

| Model      | Processing Time (s) | Processing Speed (Relative to Realtime) |
|------------|---------------------|-----------------------------------------|
| tiny       | 16.4                | x7                                      |
| base       | 25.1                | x4.8                                    |
| large-v2   | 387.5               | x0.3                                    |
| turbo      | 101.74              | x1.2                                    |


## tiny

```bash
root@ee4c85becadc:/code# time whisper sample_ru_120s.mp3 --model tiny --language ru --model_dir /cache --device cpu
/usr/local/lib/python3.9/site-packages/whisper/__init__.py:150: FutureWarning: You are using `torch.load` with `weights_only=False` (the current default value), which uses the default pickle module implicitly. It is possible to construct malicious pickle data which will execute arbitrary code during unpickling (See https://github.com/pytorch/pytorch/blob/main/SECURITY.md#untrusted-models for more details). In a future release, the default value for `weights_only` will be flipped to `True`. This limits the functions that could be executed during unpickling. Arbitrary objects will no longer be allowed to be loaded via this mode unless they are explicitly allowlisted by the user via `torch.serialization.add_safe_globals`. We recommend you start setting `weights_only=True` for any use case where you don't have full control of the loaded file. Please open an issue on GitHub for any issues related to this experimental feature.
  checkpoint = torch.load(fp, map_location=device)
/usr/local/lib/python3.9/site-packages/whisper/transcribe.py:126: UserWarning: FP16 is not supported on CPU; using FP32 instead
  warnings.warn("FP16 is not supported on CPU; using FP32 instead")
[00:00.000 --> 00:06.480]  Налитическая геометрия, раздел геометрия, в котором геометрия
[00:06.480 --> 00:09.240]  геометрия, в котором геометрия фигур, и их свостовы исследуются
[00:09.240 --> 00:12.760]  средствами альдебра. В основе этого метода лежит так называемый
[00:12.760 --> 00:18.000]  метод карденат, впервые применённый декартам в 1637 году.
[00:18.000 --> 00:21.560]  Каждому геометрия с кемы с отношением, этот метод ставит
[00:21.560 --> 00:25.320]  в соответствии некоторого равними, связывающая кардинатов
[00:25.320 --> 00:29.320]  фигуры или тему. Такой метод алгеброизация геометрических
[00:29.320 --> 00:32.520]  свостов оказался универсальность, и плодатворно применяется
[00:32.520 --> 00:37.600]  во многих естественных науках и в техники. В математике, в математике
[00:37.600 --> 00:41.140]  аналитическая геометрия является также основой для других
[00:41.140 --> 00:45.320]  разделов геометрия, например, дефренсальный алгеброидческой,
[00:45.320 --> 00:48.320]  комденатурной и вычислительной геометрия.
[00:48.320 --> 00:52.400]  Идея кардинат и уравнения к ревой была нечужда еще
[00:52.400 --> 00:57.360]  древним греком. Архимет и особенно о полоне Беркске,
[00:57.360 --> 01:00.600]  в своих сочинениях приводили так называемой симптомы
[01:00.600 --> 01:04.600]  конеческих сечений, которые вряди случаев совпадают
[01:04.600 --> 01:07.800]  с нашим уравнением. Однако дальнейшего развития
[01:07.800 --> 01:10.600]  – это идея тогда не получила, по причине невысокого
[01:10.600 --> 01:15.040]  уровня древнедрической алгебры и слабого интереса к кривым,
[01:15.040 --> 01:20.640]  отличным от прямой и окружности. Потом в Европе использовал
[01:20.640 --> 01:23.680]  кардинатное изображение для функции за вещь от времени
[01:23.680 --> 01:31.520]  Николай Аэр Ариязмский, 14 век, который называл кардинат
[01:31.520 --> 01:35.680]  в панологии с географическими, долго той широты, к этому
[01:35.680 --> 01:39.120]  время не разведите, то понятие о кардинатах уже существовало
[01:39.120 --> 01:43.040]  в странном географии. Лешающий шаг был сделан после того,
[01:43.040 --> 01:47.000]  как вет, 16 век, сконструировал символический язык для
[01:47.000 --> 01:51.040]  записью в равнении и положил начало системы символической
[01:51.040 --> 01:51.640]  алгебры.

real    0m16.338s
user    2m8.594s
sys     0m1.734s
```

## base

```bash
root@ee4c85becadc:/code# time whisper sample_ru_120s.mp3 --model base --language ru --model_dir /cache --device cpu
/usr/local/lib/python3.9/site-packages/whisper/__init__.py:150: FutureWarning: You are using `torch.load` with `weights_only=False` (the current default value), which uses the default pickle module implicitly. It is possible to construct malicious pickle data which will execute arbitrary code during unpickling (See https://github.com/pytorch/pytorch/blob/main/SECURITY.md#untrusted-models for more details). In a future release, the default value for `weights_only` will be flipped to `True`. This limits the functions that could be executed during unpickling. Arbitrary objects will no longer be allowed to be loaded via this mode unless they are explicitly allowlisted by the user via `torch.serialization.add_safe_globals`. We recommend you start setting `weights_only=True` for any use case where you don't have full control of the loaded file. Please open an issue on GitHub for any issues related to this experimental feature.
  checkpoint = torch.load(fp, map_location=device)
/usr/local/lib/python3.9/site-packages/whisper/transcribe.py:126: UserWarning: FP16 is not supported on CPU; using FP32 instead
  warnings.warn("FP16 is not supported on CPU; using FP32 instead")
[00:00.000 --> 00:11.000]  Налетическая геометра. Налетическая геометра раздел геометрия, в котором геометрический фигур и их свойство исследуется с рестами алгебра.
[00:11.000 --> 00:18.000]  В основе этого метода лежит так называемый метод координат, впервые примененный декартом в 1637 году.
[00:18.000 --> 00:27.000]  Каждому геометрическому соотношению этот метод ставит в соответствии некоторого равними, связывающие координаты фигуры или тела.
[00:27.000 --> 00:35.000]  Такой метод алгебраизации геометрических соотит оказался универсальность и плодотворно применяется во многих естественных науках и в технике.
[00:35.000 --> 00:48.000]  В математике аналетическая геометра является также основой для других разделов геометрии, например, дифференциальный алгебраической, конденоторной и вычислительной геометрии.
[00:49.000 --> 00:53.000]  Идея координат и уравнения кривой была нечуждая еще древним греком.
[00:53.000 --> 01:02.000]  Архимет, и особенно о полоне Перкский, в своих сочинениях приводили так называемые симптомы конических сечений,
[01:02.000 --> 01:06.000]  которые в ряд случаев совпадают с нашими уравними.
[01:06.000 --> 01:17.000]  Однако дальнейшего развития эта идея тогда не получила по причине невысокого уровня древнегрической алгебры и слабого интереса кривы отлично от прямой и окружности.
[01:18.000 --> 01:35.000]  Потом в Европе использовал координатное изображение для функции зависит от времени Николай Ариезомский, 14-й век, который назвал координат по аналогии с географическими долготой широты.
[01:35.000 --> 01:40.000]  К этому времени разведить понятие о координатах уже существовало в страну мини географии.
[01:40.000 --> 01:52.000]  Решающий шаг был сделан после того, как въет 16-й век, сконструировал символичный язык для записи уравнений и положил начало системной символической алгебры.

real    0m25.083s
user    3m28.938s
sys     0m2.941s
```

## large-v2

```bash
root@ee4c85becadc:/code# time whisper sample_ru_120s.mp3 --model large-v2  --language ru --model_dir /cache --device cpu
/usr/local/lib/python3.9/site-packages/whisper/__init__.py:150: FutureWarning: You are using `torch.load` with `weights_only=False` (the current default value), which uses the default pickle module implicitly. It is possible to construct malicious pickle data which will execute arbitrary code during unpickling (See https://github.com/pytorch/pytorch/blob/main/SECURITY.md#untrusted-models for more details). In a future release, the default value for `weights_only` will be flipped to `True`. This limits the functions that could be executed during unpickling. Arbitrary objects will no longer be allowed to be loaded via this mode unless they are explicitly allowlisted by the user via `torch.serialization.add_safe_globals`. We recommend you start setting `weights_only=True` for any use case where you don't have full control of the loaded file. Please open an issue on GitHub for any issues related to this experimental feature.
  checkpoint = torch.load(fp, map_location=device)
/usr/local/lib/python3.9/site-packages/whisper/transcribe.py:126: UserWarning: FP16 is not supported on CPU; using FP32 instead
  warnings.warn("FP16 is not supported on CPU; using FP32 instead")
[00:00.000 --> 00:07.080]  Аналитическая геометрия. Аналитическая геометрия – раздел геометрии, в котором геометрические
[00:07.080 --> 00:12.240]  фигуры и их свойства исследуются средствами алгебры. В основе этого метода лежит так
[00:12.240 --> 00:19.480]  называемый метод координат, впервые примененный Декартом в 1637 году. К каждому геометрическому
[00:19.480 --> 00:25.600]  соотношению этот мет ставят в соответствие некоторое уравнение, связывающее координаты фигуры
[00:25.600 --> 00:30.880]  или тела. Такой метод алгеброизации геометрических свойств оказался в универсальности и
[00:30.880 --> 00:38.480]  плодотворно применяется во многих естественных науках и в технике. В математике аналитическая
[00:38.480 --> 00:43.920]  геометрия является также основой для других разделов геометрии, например, дифференциальной,
[00:43.920 --> 00:51.040]  алгебраической, комбинаторной и вычислительной геометрии. Идея координат и уравнения кривой
[00:51.040 --> 00:58.240]  была не чужда еще древним грекам. Архимед и особенно Аполлоний Перкский в своих сочинениях
[00:58.240 --> 01:05.040]  приводили так называемые симптомы конических сечений, которые в ряде случаев совпадают с нашими
[01:05.040 --> 01:10.920]  уравнениями. Однако дальнейшего развития эта идея тогда не получила, по причине невысокого уровня
[01:10.920 --> 01:18.680]  древнегреческой алгебры и слабого интереса к кривым, отличным от прямой и окружности. Потом в
[01:18.680 --> 01:24.120]  Европе использовал координатное изображение для функции зависящей от времени Николай
[01:24.120 --> 01:33.040]  Арьезамский в XIV веке, который называл координаты по аналогии с географическими
[01:33.040 --> 01:39.640]  долготой широты. К этому времени развитие понятия о координатах уже существовало в астрономии
[01:39.640 --> 01:46.520]  и географии. Решающий шаг был сделан после того, как Виет в XVI век сконструировал символический
[01:46.520 --> 01:51.560]  язык для записи уравнений и положил начало системной символической алгебре.

real    6m27.502s
user    40m51.644s
sys     1m2.429s
```

## turbo

```bash
root@ee4c85becadc:/code# time whisper sample_ru_120s.mp3 --model turbo --language ru --model_dir /cache --device cpu
/usr/local/lib/python3.9/site-packages/whisper/__init__.py:150: FutureWarning: You are using `torch.load` with `weights_only=False` (the current default value), which uses the default pickle module implicitly. It is possible to construct malicious pickle data which will execute arbitrary code during unpickling (See https://github.com/pytorch/pytorch/blob/main/SECURITY.md#untrusted-models for more details). In a future release, the default value for `weights_only` will be flipped to `True`. This limits the functions that could be executed during unpickling. Arbitrary objects will no longer be allowed to be loaded via this mode unless they are explicitly allowlisted by the user via `torch.serialization.add_safe_globals`. We recommend you start setting `weights_only=True` for any use case where you don't have full control of the loaded file. Please open an issue on GitHub for any issues related to this experimental feature.
  checkpoint = torch.load(fp, map_location=device)
/usr/local/lib/python3.9/site-packages/whisper/transcribe.py:126: UserWarning: FP16 is not supported on CPU; using FP32 instead
  warnings.warn("FP16 is not supported on CPU; using FP32 instead")
[00:01.000 --> 00:02.620]  Аналитическая геометрия
[00:02.620 --> 00:10.380]  Аналитическая геометрия – раздел геометрии, в котором геометрические фигуры и их свойства исследуются средствами алгебры.
[00:10.880 --> 00:17.700]  В основе этого метода лежит так называемый метод координат, впервые примененный Декартом в 1637 году.
[00:18.400 --> 00:26.440]  К каждому геометрическому соотношению этот метод ставят в соответствии некоторое уравнение, связывающее координаты фигуры или тела.
[00:26.440 --> 00:34.700]  Такой метод алгебраизации геометрических соотношений доказал свою универсальность и плодотворно применяется во многих естественных науках и в технике.
[00:35.460 --> 00:47.640]  В математике аналитическая геометрия является также основой для других разделов геометрии, например, дифференциальной, алгебраической, комбинаторной и вычислительной геометрии.
[00:49.220 --> 00:53.200]  Идея координат и уравнения кривой была не чужда еще древним грекам.
[00:53.200 --> 01:05.800]  Архимед и особенно Аполлоний Бергский в своих сочинениях приводили так называемые симптомы конических сечений, которые в ряде случаев совпадают с нашими уравнениями.
[01:06.280 --> 01:17.100]  Однако дальнейшего развития эта идея тогда не получила по причине невысокого уровня древнегреческой алгебры и слабого интереса кривым, отличным от прямой и окружности.
[01:17.100 --> 01:34.660]  Потом в Европе использовал координатное изображение для функции, зависящей от времени Николай Арьезмский XIV век, который называл координаты по аналогии с географическими долготой широты.
[01:34.660 --> 01:40.340]  К этому времени развитие понятия о координатах уже существовало в астрономии географии.
[01:40.980 --> 01:51.640]  Решающий шаг был сделан после того, как Вьет XVI век сконструировал символический язык для записи уравнений и положил начало системной символической алгебре.

real    1m41.748s
user    12m9.663s
sys     1m15.220s
```