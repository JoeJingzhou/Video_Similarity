# %%
##

# %%
import json
import os
import uuid
import gradio as gr
import pandas as pd
from pathlib import Path
from gradio import State
# 设置路径
downloads_path = r'Downloads'
video_folder = os.path.join('recreat(treat)', 'recreat(treat)')
assignments_folder = 'worker_assignments(recreate_treat)'
assignments_path = os.path.join(downloads_path, assignments_folder)
video_path = os.path.join(downloads_path, video_folder)


# 读取工作人员的分配文件
def load_worker_assignments(worker_id):
    excel_path = os.path.join(assignments_path, f"{worker_id}.xlsx")
    df = pd.read_excel(excel_path, header=None, names=['id', 'title'])
    return df

# 获取视频文件路径
def get_video_path(video_id):
    video_file = f"{video_id}.mp4"
    
    full_path = os.path.join(video_path, video_file)
    if not os.path.exists(full_path):
        print(f"错误：视频文件不存在 - {full_path}")
        return None
    return full_path

current_worker_id = 3  # 这里可以根据需要修改为动态获取工作人员ID的方法
worker_df = load_worker_assignments(current_worker_id)
current_video_index = 0




json_dump_dir = Path(rf'Downloads')
json_dump_dir.parent.mkdir(parents=True, exist_ok=True)
# 获取视频文件路径
def get_video_path(video_id):
    video_file = f"{video_id}.mp4"
    full_path = os.path.join(video_path, video_file)
    if not os.path.exists(full_path):
        print(f"错误：视频文件不存在 - {full_path}")
        return None
    return full_path


def switch_to_user_info_page(us_resident, agree_to_participate, state):
    if 'session_id' not in state:
        state['session_id'] = str(uuid.uuid4())

    if us_resident and agree_to_participate:
        # If both checkboxes are checked, return a tuple that makes welcome_page invisible and user_info_page visible
        return (
            gr.update(visible=False, value=''), 
            gr.update(visible=False), 
            gr.update(visible=True),
        )
    else:
        # If not all conditions are met, you can optionally return a message or keep the current page visible
        return (
            gr.update(visible=True, value="Please confirm all required fields to proceed."), # 显示提示
            gr.update(visible=True), 
            gr.update(visible=False),
        )


def check_completion(gender, age, education, weekly_short_video_time, state):
    if gender and age and education and weekly_short_video_time:
        json_data = {
            'gender': gender,
            'age': age,
            'education': education,
            'weekly_short_video_time': weekly_short_video_time,
        }
        with open(f'{json_dump_dir}/user_info_{state["session_id"]}.json', 'a') as f:
            json.dump(json_data, f)
        return gr.update(interactive=False), gr.update(interactive=True)
    else:
        gr.Warning("Please fill in all the required fields to proceed.")
        return gr.update(interactive=True), gr.update(interactive=False)

def save_user_info(gender, age, education, weekly_short_video_time, state):
    # 逻辑处理，例如保存数据等（可选）
    json_data = {
        'gender': gender,
        'age': age,
        'education': education,
        'weekly_short_video_time': weekly_short_video_time,
    }
    with open(f'{json_dump_dir}/user_info_{state["session_id"]}.json', 'a') as f:
        json.dump(json_data, f)

    return (
        gr.update(visible=False),  # 隐藏用户信息页面
        gr.update(visible=True),   # 显示视频评分页面
    )


def switch_pages():
    return gr.update(visible=False), gr.update(visible=True)

def load_current_video():
    global current_video_index
    next_video = worker_df.iloc[current_video_index]
    video_path = get_video_path(next_video['id'])
    return video_path, next_video['title']
    

def load_next_video():
    global current_video_index
    if current_video_index < len(worker_df) - 1 and current_video_index!=0:
        current_video_index += 1
        next_video = worker_df.iloc[current_video_index]
        video_path = get_video_path(next_video['id'])
        return video_path, next_video['title']
    elif current_video_index == 0:
        next_video = worker_df.iloc[current_video_index]
        video_path = get_video_path(next_video['id'])
        current_video_index += 1
        return video_path, next_video['title']
    else:
        return None, None

def get_video_path_by_title(video_title):
    video_id = worker_df[worker_df['title'] == video_title]['id'].values[0]
    video_file = f"{video_id}.mp4"
    full_path = os.path.join(video_path, video_file)
    if not os.path.exists(full_path):
        print(f"错误：视频文件不存在 - {full_path}")
        return None
    return full_path


def check_rating(video_title, rating, state):
    print(type(state),state)
    global json_dump_dir
    json_data = {'video_title': video_title, 'rating': rating}
    if rating is None:
        gr.Warning("请先选择一个评分。")
        return gr.update(interactive=False), gr.update(interactive=True)
    else:
        with open(f'{json_dump_dir}/user_info_{state["session_id"]}.json', 'a') as f:
            json.dump(json_data, f)
        return gr.update(interactive=True), gr.update(interactive=False)
    
def load_last_video():
    global current_video_index
    

    if current_video_index > 0:
        current_video_index -= 1
        last_video = worker_df.iloc[current_video_index]
        video_path = get_video_path(last_video['id'])
        return video_path, last_video['title'], False
    else:
        return video_path, last_video['title'], True


def rate_video_next(video_title, rating):
    global current_video_index
    worker_df.loc[current_video_index, 'rating'] = rating
    
    next_video_path, next_video_title = load_next_video()
    if next_video_path:
        return (
            gr.update(visible=False),  # 隐藏评分结果提示
            next_video_path,
            next_video_title,
            gr.update(value=None, interactive=True), # 重置评分
            gr.update(interactive=True),  # 启用完成按钮
            gr.update(interactive=False),  # 禁用下一个按钮
        )
    else:
        return (
            gr.update(value="所有视频已评分完毕。感谢您的参与！", visible=True),
            None,
            "",
            gr.update(value=None, interactive=False),  # 重置评分
            gr.update(interactive=True),  # 启用完成按钮
            gr.update(interactive=False),  # 禁用下一个按钮
        )




def rate_video_last(video_title, rating):
    global current_video_index
    worker_df.loc[current_video_index, 'rating'] = rating
    last_video_path, last_video_title, is_last_one = load_last_video()
    if is_last_one:
        return (
            gr.update(value='已经是最后一个视频了', visible=True),
            last_video_path,
            last_video_title,
            gr.update(),  # 重置评分
            gr.update(interactive=False),  # 禁用评分按钮
        )
    else:
        if video_title != '' and rating is not None:
            prompts = gr.update(value=f"你对视频 '{video_title}' 的评分 ({rating}) 已保存。", visible=True)
            return (
            prompts,
            last_video_path,
            last_video_title,
            gr.update(value=None, interactive=True),  # 重置评分
            gr.update(interactive=False),  # 禁用评分按钮
        )
        else:
            prompts = gr.update(visible=False)
        return (
            prompts,
            last_video_path,
            last_video_title,
            gr.update(value=None, interactive=True),  # 重置评分
            gr.update(interactive=False),  # 禁用评分按钮
        )

#这个暂时没有放，不用管
def load_instruction_video():
    return (
        '/Users/wenhao/Documents/dataset/raw-videos/object/helicopter.mp4',  # 无关视频
        '/Users/wenhao/Documents/dataset/raw-videos/object/helicopter.mp4',  # 有关视频
    )


block_css = """
h1 {
  text-align: center;
}
h2 {
    text-align: center;
}
.column {
  padding-top: 50px;
  padding-right: 50px;
  padding-bottom: 50px;
  padding-left: 50px;
}
.vertical-radio .wrap {
    display: flex;
    flex-direction: column;
}

"""


title = 'My Survey'


title_markdown = """
<h1>My Survey</h1>
<p><center>Have a very short summary of the survey!</center></p>
"""


instruction_markdown = """
<div style="background-color: #cccccc; padding: 20px; font-size: 18px; color: black;">
    <h1>欢迎参加我们的研究</h1>
    <p>本次调查的目的是评估视频标题与视频内容的匹配度。我们希望通过您的参与，更好地了解标题和内容的相关性。</p>
    <ul>
        <li><strong>保密性</strong>：本研究是匿名的。所收集的数据不包含关于您的任何个人身份信息。通过参与，您理解并同意研究团队将使用这些数据，并且汇总结果将被发布。</li>
    </ul>
    <ul>
        <li><strong>研究时长</strong>：本研究大约需要30分钟。您可以随时选择停止参与。</li>
    </ul>
    <ul>
        <li><strong>报酬</strong>：在您完成整个研究后，您将获得4美元的参与费。所有的支付和程序将按照本实验和Prolific平台上的描述执行。</li>
    </ul>
    <ul>
        <li><strong>资格</strong>：研究开始前，我们会提供一些指导说明，请您仔细阅读。随后，我们将通过几个简单的问题来检验您是否理解了这些指导。如果您无法正确回答这些问题，将无法继续参与本研究。请勾选下方的复选框，表示您已理解并同意遵守这些规则。</li>
    </ul>
</div>

"""


instruction_page_markdown = """
<h2>Introduction</h2>
<p>Here is a long introduction to the survey. It can be multiple paragraphs long.</p>
<p>It can also contain <a href="https://www.example.com">links</a> and <strong>formatting</strong>.</p>
"""


video_rating_page_markdown = """
<!-- <h2>Video Rating</h2> -->
<div style="font-size: 20px; font-weight: bold; text-color: #232b2b;">
    <p>视频标题有多准确地反映了视频内容？</p>
</div>


"""


end_page_markdown = """
<h1>Thank you for participating in our study!</h1>
<h1>We appreciate your time and effort.</h1>
"""

def main():
    
    with gr.Blocks(title=title, theme=gr.themes.Soft(), css=block_css) as app:
        state = gr.State({})
        
        #gr.Markdown(title_markdown)
        welcome_page = gr.Group(visible=True)
        user_info_page = gr.Group(visible=False)
        instruction_page = gr.Group(visible=False)
        video_rating_page = gr.Group(visible=False)

        with welcome_page:
            gr.Markdown(instruction_markdown)
            us_resident = gr.Checkbox(label="我年满21岁")
            agree_to_participate = gr.Checkbox(
                label="我愿意参加这项研究，并同意上述规则。")
            message = gr.Textbox(visible=False)  # Correctly defined here within the same context
            submit_welcome = gr.Button("下一页")

        with user_info_page:
            #gr.Markdown(instruction_markdown)
            # gr.Checkbox(label="I am a US resident and 21 years or older.")
            # gr.Checkbox(label="I would like to participate in this study and agree to the above rules.")
            gender = gr.Radio(['男', '女', '其他'], label="性别")
            age = gr.Number(label="年龄", value=18, step=1, minimum=1)
            education = gr.Dropdown(['小学及以下', '初中', '高中', '本科', '硕士', '博士及以上'], label="教育程度")
            weekly_short_video_time = gr.Number(
                label="平均每周花在短视频平台（如抖音）上的时间（小时）", value=0, step=0.5, minimum=0)
            complete_info = gr.Button("完成")
            submit_info = gr.Button("下一页", interactive=False)

        with instruction_page:
            # with gr.Column(scale=5, elem_classes=["column"]):
            gr.Markdown(instruction_page_markdown)
            # with gr.Row():
            submit_instruction = gr.Button("开始评分")

            with gr.Row(equal_height=True, variant='panel'):
                with gr.Column(scale=5, elem_classes=["column"]):
                    low_score_video_player = gr.Video(autoplay=True, elem_id="video-player", height=500)
                    low_score_video_title = gr.Textbox(
                        label="视频标题", elem_id="video-title", value="无关的标题", interactive=False, lines=2)
                    low_score_rating = gr.Radio(
                        choices=[
                            "1. 完全不准确",
                            "2. 较不准确",
                            "3. 一般",
                            "4. 较准确",
                            "5. 非常准确"
                        ],
                        value="1. Does not match at all",  # 设置默认值
                        interactive=False,
                        show_label=True,
                        elem_classes=["vertical-radio"]  # 应用自定义样式
                    )

                with gr.Column(scale=5, elem_classes=["column"]):
                    high_score_video_player = gr.Video(autoplay=True, elem_id="video-player", height=500)
                    high_score_video_title = gr.Textbox(
                        label="视频标题", elem_id="video-title", value="有关的标题", interactive=False, lines=2)
                    high_score_rating =  gr.Radio(
                        choices=[
                            "1. 完全不准确",
                            "2. 较不准确",
                            "3. 一般",
                            "4. 较准确",
                            "5. 非常准确"
                        ],
                        # value="5. Matches exactly",  # 设置默认值
                        interactive=False,
                        show_label=True,
                        elem_classes=["vertical-radio"],  # 应用自定义样式
                        elem_id="vertical-radio"
                    )

        with video_rating_page:
            rating_result = gr.Textbox(label="评分结果", lines=2, visible=False, interactive=False)

            with gr.Row(equal_height=True,  variant='panel'):
                # Note: scale表示两列的比例，例如: 左列scale=3 右列scale=7 表示左列占3/(3+7)=30%，右列占7/(3+7)=70%
                # height表示视频播放器的高度
                with gr.Column(scale= 4, elem_classes=["column"]):
                    video_player = gr.Video(autoplay=True, elem_id="video-player", height=700)

                with gr.Column(scale= 7, elem_classes=["column"]):
                    gr.Markdown(video_rating_page_markdown)
                    video_title = gr.Label(
                        label="视频标题", elem_id="video-title", value="")
                    rating = gr.Radio(
                        choices=[
                            "1. 完全不准确",
                            "2. 较不准确",
                            "3. 一般",
                            "4. 较准确",
                            "5. 非常准确"
                        ],
                        # value="3. Has several minor discrepancies",  # 设置默认值
                        interactive=True,
                        show_label=True,
                        elem_classes=["vertical-radio"],  # 应用自定义样式
                        every=1,
                    )
                    
                
                    with gr.Row():
                        submit_show_instruction = gr.Button("查看指导说明")
                        submit_video_last = gr.Button("上一个")
                        check_opt = gr.Button("完成")
                        submit_video_next = gr.Button("下一个", interactive=False)

        submit_welcome.click(
            fn=switch_to_user_info_page,
            inputs=[us_resident, agree_to_participate, state],
            outputs=[message, welcome_page, user_info_page]
        )


        complete_info.click(
            fn=check_completion,
            inputs=[gender, age, education, weekly_short_video_time, state],
            outputs=[complete_info, submit_info]
        )

        submit_info.click(
            fn=save_user_info,
            inputs=[gender, age, education, weekly_short_video_time, state],
            outputs=[user_info_page, video_rating_page]
        ).then(lambda: load_next_video(), None, [video_player, video_title])

        submit_show_instruction.click(
            fn=switch_pages,
            inputs=[],
            outputs=[video_rating_page, instruction_page],
        ).then(lambda: load_instruction_video(), None, [low_score_video_player, high_score_video_player])

        submit_instruction.click(
            fn=switch_pages,
            inputs=[],
            outputs=[instruction_page, video_rating_page],
        )

        check_opt.click(
            fn=check_rating,
            inputs=[video_title ,rating,state],
            outputs=[submit_video_next, check_opt],
        )

        submit_video_next.click(
            fn=rate_video_next,
            inputs=[video_title, rating],
            outputs=[rating_result, video_player, video_title, rating, check_opt, submit_video_next]
        )

        submit_video_last.click(
            fn=rate_video_last,
            inputs=[video_title, rating],
            outputs=[rating_result, video_player, video_title, rating, submit_video_next]
        )

    return app


# 启动应用
if __name__ == "__main__":
    app = main()
    
    app.launch(server_port=419, share = True)





# %%



