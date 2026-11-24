#ifndef JIEBA_EDITOR_TRANSLATIONS_H
#define JIEBA_EDITOR_TRANSLATIONS_H

#include <godot_cpp/classes/translation.hpp>
#include <godot_cpp/templates/hash_map.hpp>

namespace godot {
	class JiebaEditorTranslations {
		HashMap<StringName, Ref<Translation>> translations;

	public:
		void load();
		void unload();
	};
}

#endif // JIEBA_EDITOR_TRANSLATIONS_H
