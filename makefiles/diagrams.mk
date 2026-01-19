# ===========================================
# DataForge AI - Diagram Generation
# ===========================================
# D2 diagram related targets
#
# Included by main Makefile

# -------------------------------------------
# Configuration
# -------------------------------------------
D2_THEME ?= 200
D2_LAYOUT ?= elk
D2_PAD ?= 20

DIAGRAMS_SRC_DIR := docs/diagrams
DIAGRAMS_OUT_DIR := docs/images

D2_FILES := $(wildcard $(DIAGRAMS_SRC_DIR)/*.d2)
SVG_FILES := $(patsubst $(DIAGRAMS_SRC_DIR)/%.d2,$(DIAGRAMS_OUT_DIR)/%.svg,$(D2_FILES))
PNG_FILES := $(patsubst $(DIAGRAMS_SRC_DIR)/%.d2,$(DIAGRAMS_OUT_DIR)/%.png,$(D2_FILES))

# -------------------------------------------
# Targets
# -------------------------------------------
.PHONY: diagrams diagrams-png diagrams-clean diagrams-list diagrams-watch diagrams-preview diagrams-docker

diagrams: $(SVG_FILES) ## Generate all SVG diagrams
	@printf "$(GREEN)✓ All diagrams generated successfully!$(NC)\n"

diagrams-png: $(PNG_FILES) ## Generate all PNG diagrams
	@printf "$(GREEN)✓ All PNG diagrams generated!$(NC)\n"

diagrams-clean: ## Remove all generated diagram images
	@printf "$(YELLOW)Cleaning generated diagrams...$(NC)\n"
	@rm -f $(DIAGRAMS_OUT_DIR)/*.svg $(DIAGRAMS_OUT_DIR)/*.png
	@printf "$(GREEN)✓ Cleaned$(NC)\n"

diagrams-list: ## List all diagram source files and generated images
	@printf "$(CYAN)D2 source files:$(NC)\n"
	@ls -1 $(DIAGRAMS_SRC_DIR)/*.d2 2>/dev/null | sed 's/^/  /' || echo "  (none)"
	@printf "\n"
	@printf "$(CYAN)Generated images:$(NC)\n"
	@ls -1 $(DIAGRAMS_OUT_DIR)/*.svg $(DIAGRAMS_OUT_DIR)/*.png 2>/dev/null | sed 's/^/  /' || echo "  (none)"

diagrams-watch: ## Watch for changes and auto-regenerate diagrams
	@printf "$(CYAN)Watching for diagram changes... (Ctrl+C to stop)$(NC)\n"
	@which fswatch > /dev/null || (printf "$(RED)Error: fswatch not installed. Run: brew install fswatch$(NC)\n" && exit 1)
	@fswatch -o $(DIAGRAMS_SRC_DIR)/*.d2 | xargs -n1 -I{} $(MAKE) diagrams

diagrams-preview: ## Preview a diagram with live reload (usage: make diagrams-preview FILE=architecture)
ifndef FILE
	@printf "$(RED)Error: FILE is required. Usage: make diagrams-preview FILE=architecture$(NC)\n"
	@exit 1
endif
	@printf "$(CYAN)Starting D2 preview server for $(FILE)...$(NC)\n"
	@d2 --watch --theme=$(D2_THEME) --layout=$(D2_LAYOUT) $(DIAGRAMS_SRC_DIR)/$(FILE).d2

diagrams-docker: ## Generate diagrams using Docker (no local D2 required)
	@printf "$(CYAN)Generating diagrams with Docker...$(NC)\n"
	@docker run --rm -v $(PWD):/workspace -w /workspace terrastruct/d2:latest \
		sh -c 'for f in $(DIAGRAMS_SRC_DIR)/*.d2; do \
			name=$$(basename $$f .d2); \
			echo "Generating $$name.svg..."; \
			d2 --theme=$(D2_THEME) --layout=$(D2_LAYOUT) --pad=$(D2_PAD) $$f $(DIAGRAMS_OUT_DIR)/$$name.svg; \
		done'
	@printf "$(GREEN)✓ All diagrams generated with Docker!$(NC)\n"

# -------------------------------------------
# Pattern Rules
# -------------------------------------------
$(DIAGRAMS_OUT_DIR)/%.svg: $(DIAGRAMS_SRC_DIR)/%.d2 | $(DIAGRAMS_OUT_DIR)
	@printf "$(CYAN)Generating $@...$(NC)\n"
	@d2 --theme=$(D2_THEME) --layout=$(D2_LAYOUT) --pad=$(D2_PAD) $< $@

$(DIAGRAMS_OUT_DIR)/%.png: $(DIAGRAMS_SRC_DIR)/%.d2 | $(DIAGRAMS_OUT_DIR)
	@printf "$(CYAN)Generating $@...$(NC)\n"
	@d2 --theme=$(D2_THEME) --layout=$(D2_LAYOUT) --pad=$(D2_PAD) $< $@

$(DIAGRAMS_OUT_DIR):
	@mkdir -p $@
