#################################################
# インポート
#################################################
import discord
import random
import os
from os.path import join, dirname
from dotenv import load_dotenv

#################################################
# クライアント作成(デコレータ作成のためこの位置に)
#################################################
client = discord.Client()

#################################################
# 関数
#################################################
# メッセージからオプションを抽出
def extract_options(splitmes):
    options = []
    
    # 頭文字が'-'の箇所を抽出
    for mes in splitmes:
        if mes.startswith('-'):
            options.append(mes)
    return options

# 指定外のオプションがある場合に、それらを返す
def extract_not_valid_option(options):
    not_valid_options = []
    # 指定されたオプション一覧
    valid_option    = [
        '-role_rnd',
    ]
    
    # 指定外のオプションを抽出
    for option in options:
        if option not in valid_option:
            not_valid_options.append(option)
    
    # 指定外のオプションがあればそれを返し、なければ空配列を返す
    if not not_valid_options:
        return []
    else:
        return not_valid_options

# 指定外のオプションを警告するメッセージの作成
def make_option_error_msg(not_valid_options):
    error_msg = ''
    
    for i, notValidoption in enumerate(not_valid_options):
        if i == 0:
            error_msg += '['

        error_msg += '\'' + notValidoption + '\''

        if i == len(not_valid_options) - 1:
            error_msg += ']は不明なオプションです'
    
    return error_msg

# メッセージから参加者一覧を抽出
def extract_participants(splitmes):
    participants = []

    # メッセージから参加者入力部を抽出
    participants_str = ''
    for mes in splitmes:
        if not mes.startswith('-') and not mes.startswith('!'):
            # 参加者以外に何か入力されている場合は処理を終了
            if participants_str != '': return []
            
            participants_str = mes
    
    # 参加者一覧を文字列からリストに変換
    participants = participants_str.split(',')
    return participants

# 割り当て一覧の作成
def make_assignment_list(participants, options):
    assignment_list = {}
    
    NORMAL_MODE = {
       'team1' : [
            '    ',
            '    ',
            '    ',
            '    ',
            '    '
        ],
        'team2' : [
            '    ',
            '    ',
            '    ',
            '    ',
            '    '
        ]
    }
    
    RANDOM_POTISION_MODE = {
         'team1' : [
            '    top : ',
            '    jg  : ',
            '    mid : ',
            '    adc : ',
            '    sup : '            
        ],
        'team2' : [
            '    top : ',
            '    jg  : ',
            '    mid : ',
            '    adc : ',
            '    sup : '            
        ]
    }
    
    # ロールも指定するモードの場合は、ロールも指定した割り当て一覧を作成
    if '-role_rnd' in options:
        assignment_list = RANDOM_POTISION_MODE
    else:
        assignment_list = NORMAL_MODE
    
    # 参加者が10人の場合、観戦枠を設けない
    participants_num = len(participants)
    if participants_num == 10: return assignment_list
    
    # 参加者が10人より多い場合観戦枠を設ける
    assignment_list['観戦'] = []
    
    # 10人より多い数だけ観戦枠を追加する
    extra_people_num = participants_num - 10
    for i in range(extra_people_num):
        assignment_list['観戦'].append('    ')
    
    return assignment_list

#################################################
# デコレータ
#################################################

# 起動時に動作する処理
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知を表示
    print('ログインしました')

# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    
    # メッセージ送信者がBotだった場合は無視する
    if message.author.bot: return
    
    # メッセージの内容を配列に格納
    splitmes = message.content.split()
    
    # bot宛のメッセージじゃない場合は処理を終了
    if splitmes[0] != '!lcm': return
    
    # オプションを抽出
    options = extract_options(splitmes)

    # 使用できないオプションがある場合、エラーメッセージを出力し処理を終了
    not_valid_options = extract_not_valid_option(options)
    if not_valid_options:
        await message.channel.send(make_option_error_msg(not_valid_options))
        return

    # 参加者一覧を抽出
    participants = extract_participants(splitmes)

    # 正しく入力されていない場合はエラー
    if not participants:
        await message.channel.send('余計な文字が含まれています')
        return
    # 10人以下の場合はエラー
    elif len(participants) < 10:
        await message.channel.send('振り分けには10人以上必要です')
        return

    # 人数分の割り当て一覧の作成
    assignment_list = make_assignment_list(participants, options)

    # 割り当て一覧に参加者を割り当てる
    result = ''
    random.shuffle(participants)
    for team, potisions in assignment_list.items():
        result += '■' + team + '\n'
        
        for potision in potisions:
            participant = random.choice(participants)
            participants.remove(participant)
            result += potision + participant + '\n'
        result += '\n'
        
    # 割り当て結果の表示
    await message.channel.send(result)
    
#################################################
# 実行文
#################################################
# Botの起動とDiscordサーバーへの接続
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
client.run(BOT_TOKEN)