from typing import Dict, Union, List, Tuple
from textwrap import wrap
import pathlib
import json
import os
import datetime as dt
from statistics import mean
import pandas as pd
import numpy as np
import matplotlib

matplotlib.use("Agg")
from matplotlib import pyplot as plt
import matplotlib.colors as mcolors
from PIL import Image
import weasyprint
from jinja2 import Environment, FileSystemLoader


def generate_interview_report(payload: Dict[str, Dict[str, Union[float, int]]]) -> None:
    """
    Generate the interviewer assessment report by parsing the payload

    The report will analyze and provide relevant questions based on the strengths and weaknesses of the candidate

    Args:
        param1(Dict[str, Dict[str, int | str]]): The candidate's profile and assessment results

    Returns:
        None

    Raises:
        TypeError: Must receieve nested dictionaries as an argument

    Notes:
        The PDF report generated is stored in the results directory
    """

    _validate_payload(payload)
    dict_candidate, dict_scores = _parse_payload(payload)
    dict_scores = _modify_scores(dict_scores)
    _generate_bar_charts(dict_scores)
    _generate_spider_plot(dict_scores)
    _generate_colorbar_plots(dict_scores)
    _generate_final_report(dict_candidate, dict_scores)
    _delete_temp_files()


def _validate_payload(
    payload: Dict[str, Union[str, Dict[str, Union[float, int, str]]]]
) -> None:
    """
    Data validation step to make sure that the input is of the right type

    Args:
        param1(Dict[str, Union[str, Dict[str, Union[float, int, str]]]]): The candidate's profile and assessment results

    Returns:
        None

    Raises:
        TypeError: Must receieve nested dictionaries as an argument
    """
    if not isinstance(payload, dict):
        raise TypeError(
            "Input must be nested dictionaries with values as either string, int, or float"
        )

    stack = [payload]
    while stack:
        current_dict = stack.pop()

        for key, value in current_dict.items():
            if not isinstance(key, str):
                raise TypeError("Input must be nested dictionaries with keys as string")

            if isinstance(value, dict):
                stack.append(value)
            elif not (
                isinstance(value, float)
                or isinstance(value, int)
                or isinstance(value, str)
            ):
                raise TypeError(
                    "Input must be nested dictionaries with values as either string, int, or float"
                )


def _parse_payload(
    payload: Dict[str, Dict[str, Union[float, int]]]
) -> Tuple[Dict[str, str], Dict[str, Union[float, int]]]:
    """
    Parses the payload and seperates the data into two dictionaries. One represents the candidate's profile,
    and the other represents the scores

    Args:
        param(Dict[str, Dict[str, Union[float, int]]]): nested dictionaries of the candidate's profile
        and assessment scores

    Returns:
        Tuple[Dict[str, str], Dict[str, Union[float, int]]]: tuple of dictionaries. First entry
        is a dictionary representing the candidate's profile, and the second entry is a dictionary
        representing the scores received
    """

    return (payload.pop("candidate_profile"), payload)


def _modify_scores(
    dict_scores: Dict[str, Union[float, int]]
) -> Dict[str, Dict[str, Union[float, int]]]:
    """
    Modify the scores dictionary to make the data more manageable

    Args:
        param1(Dict[str, Dict[str, int | str]]): The candidate's profile and assessment results

    Returns:
        Dict[str, Dict[str, Union[float, int]]]:
    """
    path_focus_area = (
        pathlib.Path(__file__).parent.parent / "resources" / "focus_area.json"
    )
    with open(path_focus_area) as file:
        dict_focus_area = json.load(file)

    dict_modified_scores = {key: {} for key in dict_focus_area.keys()}

    for skill, score in dict_scores.items():
        for focus_area, list_skills in dict_focus_area.items():
            if skill in list_skills:
                dict_modified_scores[focus_area][skill] = score

    return dict_modified_scores


def _generate_bar_charts(dict_scores: Dict[str, Dict[str, Union[float, int]]]) -> None:
    """
    Creates bar graphs for all focus areas based on the individual's self-assessment and save the
    static image to the tmp folder

    Args:
        param1(Dict[str, Dict[str, int | str]]): The candidate's profile and assessment results

    Returns:
        None
    """
    for focus_area, dict_skills in dict_scores.items():
        filename_ending = focus_area + ".jpg"
        path_focus_area = (
            pathlib.Path(__file__).parent.parent
            / "tmp"
            / filename_ending
        )

        categories = ["\n".join(category.split(" ")) for category in dict_skills.keys()]
        values = list(dict_skills.values())

        fig, ax = plt.subplots(figsize=(14, 6))
        ax_bar = ax.bar(categories, values, alpha=0.2)

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_position(("outward", 5))
        ax.bar_label(ax_bar, fontsize=12, padding=5)

        plt.rcParams["font.family"] = "sans-serif"
        plt.rcParams["font.sans-serif"] = "Helvetica"
        plt.rcParams["axes.edgecolor"] = "#333F4B"
        plt.rcParams["axes.linewidth"] = 0.8
        plt.rcParams["xtick.color"] = "#333F4B"

        plt.title(focus_area, fontsize=25)
        plt.xticks(fontsize=12)
        plt.yticks([])
        plt.tight_layout()
        plt.savefig(path_focus_area, format="jpg")
        plt.clf()

    matplotlib.pyplot.close()


def _generate_spider_plot(dict_scores: Dict[str, Dict[str, Union[float, int]]]) -> None:
    """
    Creates spidersplot graph that displays the self-assessment scores

    Args:
        param(Dict[str, Dict[str, Union[float, int]]]): a nested dictionary that corresponds to
        the score receieved for each focus area/skill

    Returns:
        None
    """
    categories = ["\n".join(wrap(category, 15)) for category in dict_scores.keys()]

    list_scores = [mean(skills.values()) for skills in dict_scores.values()]
    list_scores = list_scores + list_scores[:1]

    N = len(categories)
    PI = 3.14592

    # define color scheme for up to 10 comparisons
    color = "#429bf4"  # (Blue)

    angles = [n / float(N) * 2 * PI for n in range(N)]
    angles += angles[:1]

    plt.rc("figure", figsize=(10, 10))

    ax = plt.subplot(1, 1, 1, polar=True)

    ax.set_theta_offset(PI / 2)
    ax.set_theta_direction(-1)
    ax.set_ylim(0, 10)

    plt.xticks(angles[:-1], categories, color="black", size=10)
    ax.tick_params(axis="x", pad=10)

    ax.set_rlabel_position(0)
    plt.yticks([1, 10], ["1", "10"], color="black", size=10)
    plt.ylim(0, 10)

    ax.plot(angles, list_scores, color=color, linewidth=1, linestyle="solid")
    ax.fill(angles, list_scores, color=color, alpha=0.3)

    for i, (angle, radius) in enumerate(zip(angles[:-1], list_scores[:-1])):
        x = angle
        y = radius

        if x >= 0 and x <= 1.5:
            xytext = (0, 8)
        elif x <= 3:
            xytext = (8, 0)
        elif x < 4.5:
            xytext = (0, -8)
        else:
            xytext = (-8, 0)

        ax.annotate(np.round(list_scores[i],1), xy=(x, y), xytext=xytext, textcoords='offset points', ha='center', va='center')

    path_spiderplot_graph = (
        pathlib.Path(__file__).parent.parent
        / "tmp"
        / "focus_area_spider_plot.jpg"
    )
    plt.savefig(path_spiderplot_graph, format="jpg")

    # crop the left and right sides of the image
    image = Image.open(path_spiderplot_graph)
    width, height = image.size
    crop_width = int(width * 0.25)
    left = crop_width
    top = 0
    right = width - crop_width
    bottom = height
    cropped_image = image.crop((left, top, right, bottom))
    cropped_image.save(path_spiderplot_graph)

    matplotlib.pyplot.close()


def _generate_colorbar_plots(
    dict_scores: Dict[str, Dict[str, Union[float, int]]]
) -> None:
    """
    Creates horizontal gauge charts based on the individual's scores.

    Args:
        param(Dict[str, Dict[str, Union[float, int]]]): a nested dictionary that corresponds
        to the score receieved for each focus area/skill

    Returns:
        None
    """
    path_skill_range = (
        pathlib.Path(__file__).parent.parent / "resources" / "skill_range.csv"
    )
    df_skill_range = pd.read_csv(path_skill_range)

    fig = plt.figure(figsize=(8, 2))
    ax = fig.add_axes([0.1, 0.2, 0.8, 0.4])
    ax2 = fig.add_axes([0.1, 0.1, 0.8, 0.1])
    ax3 = fig.add_axes([0.1, 0.6, 0.8, 0.1])

    left_color = "#FCBEC1"
    right_color = "#D9FBC8"
    center_color = "#F4F4F4"

    # Create a colormap for the left half (green to white)
    cmap_left = mcolors.LinearSegmentedColormap.from_list(
        "LeftCmap", [left_color, center_color]
    )

    # Create a colormap for the right half (white to red)
    cmap_right = mcolors.LinearSegmentedColormap.from_list(
        "RightCmap", [center_color, right_color]
    )

    # white cmap
    cmap_white = mcolors.LinearSegmentedColormap.from_list(
        "WhiteCmap", ["white", "white"]
    )

    # Combine the left and right colormaps
    colors = np.vstack(
        (cmap_left(np.linspace(0, 1, 256)), cmap_right(np.linspace(0, 1, 256)))
    )
    cmap_custom = mcolors.ListedColormap(colors)

    for skill_dict in dict_scores.values():
        for skill, score in skill_dict.items():
            min_gauge_value = df_skill_range.loc[
                df_skill_range["skills"] == skill, "Min"
            ].values[0]
            max_gauge_value = df_skill_range.loc[
                df_skill_range["skills"] == skill, "Max"
            ].values[0]
            r1_gauge_value = df_skill_range.loc[
                df_skill_range["skills"] == skill, "R1"
            ].values[0]
            r2_gauge_value = df_skill_range.loc[
                df_skill_range["skills"] == skill, "R2"
            ].values[0]

            guage_range = np.linspace(min_gauge_value, max_gauge_value, 512)

            norm = matplotlib.colors.Normalize(
                vmin=guage_range[0], vmax=guage_range[-1]
            )

            cbar = matplotlib.colorbar.ColorbarBase(
                ax,
                cmap=cmap_custom,
                norm=norm,
                orientation="horizontal",
                boundaries=guage_range,
            )

            cbar2 = matplotlib.colorbar.ColorbarBase(
                ax2,
                cmap=cmap_white,
                norm=norm,
                orientation="horizontal",
                boundaries=guage_range,
            )

            cbar3 = matplotlib.colorbar.ColorbarBase(
                ax3,
                cmap=cmap_white,
                norm=norm,
                orientation="horizontal",
                boundaries=guage_range,
            )

            cbar.outline.set_visible(False)
            cbar2.outline.set_visible(False)
            cbar3.outline.set_visible(False)

            ax.axvspan(score - 0.1, score + 0.1, 0, 1, facecolor="#000000")
            ax2.axvspan(score - 0.1, score + 0.1, 0, 1, facecolor="#000000")
            ax3.axvspan(score - 0.1, score + 0.1, 0, 1, facecolor="#000000")

            file_name = skill + ".jpg"
            path_skill_gauge_chart = (
                pathlib.Path(__file__).parent.parent / "tmp" / file_name
            )

            ax.set_xticks([])
            ax2.set_xticks([])
            ax3.set_xticks([])

            annotation = plt.annotate(
                "1", xy=(0.1, 0.1), xycoords="figure fraction", ha="center", fontsize=14
            )
            annotation2 = plt.annotate(
                "10",
                xy=(0.9, 0.1),
                xycoords="figure fraction",
                ha="center",
                fontsize=14,
            )
            annotation3 = plt.annotate(
                str(score),
                xy=(score / 11, 0.75),
                xycoords="figure fraction",
                ha="center",
                fontsize=14,
            )

            plt.savefig(path_skill_gauge_chart, format="jpg")

            annotation.remove()
            annotation2.remove()
            annotation3.remove()


def _generate_final_report(
    dict_candidate: Dict[str, str], dict_scores: Dict[str, Dict[str, Union[float, int]]]
) -> None:
    """
    Generate final report by first generating the html code and then the corresponding pdf report

    Args:
        param1(Dict[str, str]): a dictionary representing the candidate's scores
        param2(Dict[str, Dict[str, Union[float, int]]]): a nested dictionary that corresponds to
        the score receieved for each focus area/skill

    Returns:
        None
    """
    _generate_html(dict_candidate, dict_scores)
    _generate_pdf(dict_candidate)


def _generate_html(
    dict_candidate: Dict[str, str], dict_scores: Dict[str, Dict[str, Union[float, int]]]
) -> None:
    """
    Render the html file by using jinja2 and the pilot.html file to customize the html file
    based on the specific candidate's scores

    Args:
        param1(Dict[str, str]): a dictionary representing the candidate's scores
        param2(Dict[str, Dict[str, Union[float, int]]]): a nested dictionary that corresponds
        to the score receieved for each focus area/skill

    Returns:
        None
    """
    path_templates = pathlib.Path(__file__).parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(path_templates))
    template = env.get_template("pilot.html")

    dict_bottom_top_skills = _get_bottom_and_top_skills(dict_scores)

    payload = {
        "dict_candidate": dict_candidate,
        "dict_scores": dict_scores,
        "dict_bottom_top_skills": dict_bottom_top_skills,
        "dict_bottom_top_skills_text": _get_text_for_top_and_bottom_skills(
            dict_bottom_top_skills
        ),
        "dict_all_skills_description": _get_all_skills_description(),
        "date": dt.date.today(),
    }

    rendered_template = template.render(payload)

    path_rendered_template = (
        pathlib.Path(__file__).parent.parent / "templates" / "rendered_template.html"
    )

    with open(path_rendered_template, "w") as file:
        file.write(rendered_template)


def _get_bottom_and_top_skills(
    dict_scores: Dict[str, Dict[str, Union[float, int]]]
) -> Dict[str, List[str]]:
    """
    Helper function to determine the bottom 3 and top 3 skills

    Args:
        param1(Dict[str, Dict[str, Union[float, int]]]): a nested dictionary that corresponds
        to the score receieved for each focus area/skill

    Returns:
        Dict[str, List[str]]: Dictionary consisting of the bottom 3 skills and top 3 skills
    """
    list_skill_scores = []
    for skill_dict in dict_scores.values():
        for skill, score in skill_dict.items():
            list_skill_scores.append((skill, score))

    sorted_list_skill_scores = sorted(list_skill_scores, key=lambda x: x[1])
    list_bottom_skills = [x[0] for x in sorted_list_skill_scores[:3] if x[1] < 6.5]
    list_top_skills = [x[0] for x in sorted_list_skill_scores[-3:] if x[1] > 6.5]
    return {"bottom_skills": list_bottom_skills, "top_skills": list_top_skills}


def _get_text_for_top_and_bottom_skills(
    dict_bottom_top_skills: Dict[str, List[str]]
) -> Dict[str, Dict[str, Dict[str, str]]]:
    """
    Helper function to retrieve the text from report_dynamic_txt.json file based on the top 3 and bottom 3 skills

    Args:
        param1(Dict[str, List[str]]): Dictionary consisting of the bottom 3 skills and top 3 skills

    Returns:
        Dict[str, Dict[str, Dict[str, str]]]: a dictionary that maps top and bottom skills to the respective text
    """
    path_skills_json = (
        pathlib.Path(__file__).parent.parent / "resources" / "skills.json"
    )
    with open(path_skills_json) as file:
        dict_skills_text = json.load(file)

    dict_bottom_top_skills_text = {}
    for skill_position, list_skill in dict_bottom_top_skills.items():
        dict_bottom_top_skills_text[skill_position] = {}
        for skill in list_skill:
            dict_bottom_top_skills_text[skill_position][skill] = {}
            for field, value in dict_skills_text[skill].items():
                dict_bottom_top_skills_text[skill_position][skill][field] = value

    return dict_bottom_top_skills_text


def _get_all_skills_description() -> Dict[str, Dict[str, str]]:
    """
    Helper function to get the descriptions of all skills

    Args:
        None

    Returns:
        Dict[str, Dict[str, str]]: dictionary representing all focus areas and their corresponding
        skills and their corresponding descriptions
    """
    path_skills_json = (
        pathlib.Path(__file__).parent.parent / "resources" / "skills.json"
    )
    with open(path_skills_json) as file:
        dict_skills_text = json.load(file)

    path_focus_area_json = (
        pathlib.Path(__file__).parent.parent / "resources" / "focus_area.json"
    )
    with open(path_focus_area_json) as file:
        dict_focus_area = json.load(file)

    dict_skills_text_cleaned = {key: {} for key in dict_focus_area.keys()}

    for focus_area, list_skills in dict_focus_area.items():
        for skill in list_skills:
            dict_skills_text_cleaned[focus_area][skill] = dict_skills_text[skill][
                "description"
            ]

    return dict_skills_text_cleaned


def _generate_pdf(dict_candidate: Dict[str, str]) -> None:
    """
    Creates the final PDF file and saves to the results folder

    Args:
        param1(Dict[str, int | str]]): The candidate's profile

    Returns:
        None
    """
    name, company = dict_candidate["name"].replace(" ", "_"), dict_candidate[
        "company_name"
    ].replace(" ", "_")
    date_today_string = dt.date.today().strftime("%Y-%m-%d")
    report_filename = "_".join([name, company, date_today_string])
    report_filename += ".pdf"

    path_html_file = (
        pathlib.Path(__file__).parent.parent / "templates" / "rendered_template.html"
    )
    path_pdf_report = pathlib.Path(__file__).parent.parent / "results" / report_filename

    weasyprint.HTML(path_html_file).write_pdf(path_pdf_report)


def _delete_temp_files() -> None:
    """
    Deletes all files that were created except for the PDF file (images/graphs and html/css)

    Args:
        None

    Returns:
        None
    """
    directory = pathlib.Path(__file__).parent.parent / "tmp"

    # Get a list of all files in the directory
    file_list = os.listdir(directory)

    # Iterate over the file list and delete each file
    for filename in file_list:
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

    path_html_file = (
        pathlib.Path(__file__).parent.parent / "templates" / "rendered_template.html"
    )
    os.remove(path_html_file)

if __name__ == '__main__':
    dict_data =   {
      "Purpose-driven": 6.5, 
      "Self-directedness": 7.5, 
      "Big Picture Thinking": 7.25, 
      "Exploring perspectives and alternatives": 4.5, 
      "Empowering others": 6.0, 
      "Role Modeling": 8.25, 
      "Understanding one's emotions": 4.0, 
      "Self-control and regulation": 6.5, 
      "Speaking with conviction": 7.5, 
      "Empathetic": 4.0, 
      "Motivating and inspiring others": 8.0, 
      "Coaching": 5.0, 
      "Resilience": 8.0, 
      "Energy, passion and optimism": 6.5, 
      "Courage and risk-taking": 7.0, 
      "Driving change and innovation": 4.0, 
      "Dealing with uncertainty": 7.0, 
      "Instilling Trust": 6.0, 
      "Openness to feedback": 7.5, 
      "Collaboration Skills": 4.0, 
      "Fostering inclusiveness": 5.5, 
      "Organizational awareness": 6.0, 
      "Vision Alignment": 4.5, 
      "Time management and prioritization": 6.0, 
      "Promoting a culture of respect": 7.0, 
      "Unconventional approach": 5.0, 
      "Adaptability": 4.0, 
      "Attention to detail": 7.0, 
      "Planning": 6.5, 
      "Project management": 7.0, 
      "Critical Thinking": 8.0, 
      "Strategic Thinking": 7.5, 
      "Ownership and accountability": 5.5, 
      "Developing others": 7.0, 
      "Contextualization of knowledge": 6.0, 
      "candidate_profile": 
      {
          "name": "employee name", 
          "company_name": "company name"
      }
  }
    generate_interview_report(dict_data)