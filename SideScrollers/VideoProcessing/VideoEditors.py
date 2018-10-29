from moviepy.editor import VideoFileClip, concatenate_videoclips
import datetime


class VideoEditor:
	def __init__(self, video, timestamps):
		"""Initialization of the class
		:param video: Path to a video
		:type video: str
		:param templates: Path to templates
		:type templates: list
		"""
		self.video = video
		self.timestamps = timestamps

	def edit(self):

		def find_index(index_start, number_skipped, corpus, search_term):
			for indexer, i in enumerate(corpus[index_start:][number_skipped:]):
				if search_term in i:
					return indexer + number_skipped + index_start
			return -1

		text_base = VideoFileClip("JumpOrMove.mp4")
		org_video = VideoFileClip(self.video)

		choice_list = {}
		index = 0
		ARBITRARY_SKIP = 3

		print("======= TIME STAMP INFORMATION =======")
		print(f"TIMESTAMPS DATA: {self.timestamps}")
		print(f"TOTAL NUMBER OF TIME STAMPS: {len(self.timestamps)}")
		print(f"TOTAL NUMBER OF JUMPS FOUND: {len([i for i in self.timestamps if 'j' in i])}")
		print(f"TOTAL NUMBER OF RUNS FOUND: {len([i for i in self.timestamps if 'r' in i])}")
		print("======= END =======")

		def string_to_timedelta(org_string):
			return_value = datetime.datetime.strptime(org_string, "%H:%M:%S.%f")
			return_value = datetime.timedelta(hours=return_value.hour,
			                                  minutes=return_value.minute,
			                                  seconds=return_value.second,
			                                  microseconds=return_value.microsecond)
			return return_value

		no_choices = 0

		print("DEVELOPING FRAME INDICES")
		while index + 1 < len(self.timestamps):
			cur_type = 'j' if 'j' in self.timestamps[index] else 'r'
			next_type = 'j' if 'j' in self.timestamps[index + 1] else 'r'

			if cur_type == 'j' and next_type == 'r':
				no_choices += 1

				direct_next_run = self.timestamps[index + 1]
				# a_few_skipped_run = find_index(index, ARBITRARY_SKIP, self.timestamps, 'r')
				a_few_skipped_run = find_index(index, ARBITRARY_SKIP, self.timestamps, 'j')
				if a_few_skipped_run == -1: break
				choice_list[self.timestamps[index]] = (self.timestamps[a_few_skipped_run], direct_next_run)
				# choice_list[self.timestamps[index]] = (self.timestamps[a_few_skipped_run], self.timestamps[a_few_skipped_run])
				index = a_few_skipped_run

			elif cur_type == "j" and next_type == "j":
				# finds the middle point between two jumps (it's assumed that you have to land before you can jump again)
				no_choices += 1

				init_jump = string_to_timedelta(self.timestamps[index].replace('j', '').lstrip(' '))
				last_jump = string_to_timedelta(self.timestamps[index + 1].replace('j', '').lstrip(' '))

				pos = str((init_jump + last_jump) / 2)

				next_run_index = find_index(index, ARBITRARY_SKIP, self.timestamps, 'r')
				next_jump_index = find_index(index, ARBITRARY_SKIP, self.timestamps, 'j')

				if next_run_index == -1 or next_jump_index == -1: break

				print(self.timestamps[next_jump_index])

				next_run = self.timestamps[next_run_index].replace('r', '').lstrip(' ')
				next_jump = self.timestamps[next_jump_index].replace('j', '').lstrip(' ')

				choice_list[pos] = (next_run, next_jump)

				next_run = string_to_timedelta(next_run)
				next_jump = string_to_timedelta(next_jump)

				if next_run > next_jump:
					index = next_run_index
				elif next_jump > next_run:
					index = next_jump_index

			elif cur_type == "r" and next_type == "j":
				no_choices += 1
				direct_next_jump = self.timestamps[index + 1]
				skipped_to_run = find_index(index, ARBITRARY_SKIP, self.timestamps, 'r')
				if skipped_to_run == -1: break
				choice_list[self.timestamps[index]] = (self.timestamps[skipped_to_run], direct_next_jump)
				index = skipped_to_run

			elif cur_type == "r" and next_type == "r":
				index += 1

		last_end = 0
		edit_list = []
		print(f"TOTAL NUMBER OF DECISIONS MADE: {no_choices}")
		text_base = text_base.subclip(0, 2)
		for index, items_at_index in enumerate(choice_list.items()):
			starts = items_at_index[
				0]  # the current key in the index (representing the timestamp of when a decision starts)
			edits = items_at_index[1][1]  # the current values indexed at a pre-defined choice
			print("==== THIS IS CURRENT CLIP EXPORT INFO ====")
			print(f"THE CLIP START TIME: {last_end}")
			print(f"THE CLIP END TIME: {starts}")
			print(f"THE SECOND HALF OF THE CLIP START TIME {edits}")
			try:
				print(f"THE SECOND HALF OF THE CLIP END TIME {list(choice_list.keys())[index + 1]}")
			except IndexError:
				pass
			print("=== END ===")

			inital_cut = org_video.subclip(t_start=last_end, t_end=starts)
			edit_list.append(inital_cut)
			edit_list.append(text_base)

			try:
				last_end = list(choice_list.keys())[index + 1]
			except IndexError:
				break

			choice_cut = org_video.subclip(t_start=edits,
			                               t_end=str(string_to_timedelta(
				                               edits.replace('r', '').replace('j', '').lstrip(' ')) + datetime.timedelta(seconds=1)
			                                         )
			                               )
			edit_list.append(choice_cut)

		print("=== OUTPUT INFORMATION ===")
		print(f"=== CHOICE COUNT: {no_choices} ===")
		print("=== END ===")
		print(edit_list)
		final = concatenate_videoclips(edit_list, method="compose")
		final.write_videofile("Ori_edit_jumping_choices_only.mp4")


