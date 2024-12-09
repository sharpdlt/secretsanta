<template>
  <div>
    <h3 class="send__title with__title">{{ label }}</h3>
    <div class="send__direction tag__text-area" @click="focusOnClick">
      <div class="send__tags">
        <span class="send__tag-placeholder" v-if="checkEmpty"
          >Разделяй желания запятой (,)</span
        >
        <TransitionGroup name="tags">
          <span
            v-for="tag in tags"
            class="send__tag"
            :key="tag"
            @click="removeTag(tag)"
            >{{ tag }}</span
          >
        </TransitionGroup>

        <div
          contenteditable="true"
          class="send__input send__input-editable"
          ref="wishListInputRef"
          @input="enterText"
          @keydown="handleKeyDown"
          @blur="handleBlur"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  label: {
    type: String,
    required: true,
  },
});

const emit = defineEmits(["updateTags"]);
const tags = ref([]);
const textInput = ref("");
const wishListInputRef = ref(null);

const checkEmpty = computed(
  () => tags.value.length === 0 && textInput.value.length === 0
);
const enterText = (event) => {
  const hasComma = event.data === ",";
  const data = event.target.innerText.trim();
  textInput.value = data;

  if (hasComma && textInput.value !== "") {
    const tag = textInput.value.replace(/,$/, "").trim();
    if (tag !== "") {
      tags.value.push(tag);
      emit("updateTags", tags.value);
    }
    event.target.innerHTML = "";
    textInput.value = "";
  } else if (hasComma) {
    event.target.innerHTML = "";
    textInput.value = "";
  }
};

const handleKeyDown = (event) => {
  if (event.key === "Backspace" && textInput.value === "") {
    tags.value.pop();
    emit("updateTags", tags.value);
  }
  if (event.key === "Enter" && textInput.value !== "") {
    tags.value.push(textInput.value);

    event.target.innerHTML = "";
    textInput.value = "";
    emit("updateTags", tags.value);
  }
};

const handleBlur = (event) => {
  if (textInput.value !== "") {
    tags.value.push(textInput.value);

    event.target.innerHTML = "";
    textInput.value = "";
    emit("updateTags", tags.value);
  }
};

const focusOnClick = (event) => {
  if (event.target.className === "send__tag") {
    return;
  }
  wishListInputRef.value.focus();
};

const removeTag = (tag) => {
  const index = tags.value.findIndex((t) => t === tag);
  tags.value.splice(index, 1);

  emit("updateTags", tags.value);
};
</script>
