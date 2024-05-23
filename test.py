import survey  # pip install survey

colour_list = ['red', 'green', 'blue', 'pink', 'silver', 'magenta']

index = survey.routines.select('Favorite colour? ',  options = colour_list,  focus_mark = '> ',  evade_color = survey.colors.basic('yellow'))
print(f'Answered {colour_list[index]}.')