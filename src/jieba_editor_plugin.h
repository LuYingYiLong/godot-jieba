#ifndef JIEBA_EDITOR_PLUGIN_H
#define JIEBA_EDITOR_PLUGIN_H

#include "jieba_editor_translations.h"
#include "resource_importer_jieba.h"

#include <godot_cpp/classes/editor_plugin.hpp>

namespace godot {
	class JiebaEditorDock;

	class JiebaEditorPlugin : public EditorPlugin {
		GDCLASS(JiebaEditorPlugin, EditorPlugin)

	private:
		JiebaEditorTranslations editor_translations;
		Ref<ResourceImporterJieba> importer;
		JiebaEditorDock* dock = nullptr;

	protected:
		static void _bind_methods();

	public:
		JiebaEditorPlugin();
		~JiebaEditorPlugin();

		void _enter_tree() override;
		void _exit_tree() override;
	};
}

#endif // JIEBA_EDITOR_PLUGIN_H
