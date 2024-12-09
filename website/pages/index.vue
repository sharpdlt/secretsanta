<template>
  <main class="l-main">
    <!--========== HOME ==========-->
    <section class="home" id="home">
      <div class="home__container bd-container bd-grid">
        <div class="home__img">
          <img src="/img/home.png" alt="" />
        </div>

        <div class="home__data">
          <h1 class="home__title">Стань Тайным Сантой – Подари Улыбку!</h1>
          <p class="home__description">
            Организуй незабываемый обмен подарками с друзьями, коллегами или
            семьей. Тайный Санта — это простой способ сделать праздник волшебным
            и душевным.
          </p>
          <a href="#send" class="button">Начать</a>
        </div>
      </div>
    </section>

    <!--========== SHARE ==========-->
    <section class="share section bd-container" id="share">
      <div class="share__container bd-grid">
        <div class="share__data">
          <h2 class="section-title-center">Поделись волшебством праздника!</h2>
          <p class="share__description">
            "Пригласи друзей, семью или коллег стать частью Тайного Санты.
            Скопируй ссылку и поделись радостью праздника – чем больше
            участников, тем веселее!"
          </p>
          <button
            type="button"
            class="button"
            @click="copyLink"
            :disabled="copyLinkSuccess"
          >
            {{
              copyLinkSuccess ? "Ссылка скопирована!" : "Скопировать ссылку!"
            }}
          </button>
        </div>

        <div class="share__img">
          <img src="/img/shared.png" alt="" />
        </div>
      </div>
    </section>

    <!--========== DECORATION ==========-->
    <section class="decoration section bd-container" id="decoration">
      <h2 class="section-title">Как работает Тайный Санта?</h2>
      <div class="decoration__container bd-grid">
        <div class="decoration__data">
          <img src="/img/decoration1.png" alt="" class="decoration__img" />
          <h3 class="decoration__title">Заполни свое имя и почту</h3>
          <p>Укажи данные, чтобы участвовать в обмене подарками</p>
        </div>

        <div class="decoration__data">
          <img src="/img/decoration2.png" alt="" class="decoration__img" />
          <h3 class="decoration__title">Расскажи о своих предпочтениях</h3>
          <p>Напиши, что ты хотел бы получить, и что точно не нужно!</p>
        </div>

        <div class="decoration__data">
          <img src="/img/decoration3.png" alt="" class="decoration__img" />
          <h3 class="decoration__title">Подготовься к сюрпризу!</h3>
          <p>
            Отправь форму и жди, когда система случайно выберет твоего Тайного
            Санту. Пора готовиться дарить и получать радость!
          </p>
        </div>
      </div>
    </section>

    <!--========== SEND GIFT ==========-->
    <section class="send section" id="send">
      <div class="send__container bd-container bd-grid">
        <div class="send__content">
          <h2 class="section-title-center send__title">
            Заполни данные для участия
          </h2>
          <p class="send__description">
            Укажи свое имя, почту и оставь пожелания, чтобы твой Тайный Санта
            знал, что подарить. Введенные данные помогут сделать праздник
            незабываемым!
          </p>
        </div>

        <div class="send__img">
          <img src="/img/send.png" alt="" />
        </div>

        <form action="" class="wish__form">
          <div class="wish__form-common">
            <div :class="['send__direction']">
              <input
                type="text"
                placeholder="Фамилия Имя"
                class="send__input"
                v-model="fullname"
              />
            </div>
            <div :class="['send__direction', { shake: disabled }]">
              <input
                type="email"
                placeholder="Твоя почта"
                class="send__input"
                v-model="email"
              />
              <span v-if="validateEmail">✅</span>
              <span v-else-if="!validateEmail && email.length > 0">⛔</span>

              <Transition>
                <span v-if="errorMessage" class="validation-error">{{
                  errorMessage
                }}</span>
              </Transition>
              <!-- <a href="#" class="button">Send</a> -->
            </div>
          </div>
          <div class="wish__table">
            <WishInput
              class="with__table-col"
              label="Чего бы я хотел? 🤔"
              @update-tags="updateIWantTags"
            />
            <WishInput
              class="with__table-col"
              label="Чего я точно не хочу 👎"
              @update-tags="updateIDontWantTags"
            />
          </div>
          <div class="send__button">
            <button
              class="button"
              type="submit"
              @click.prevent="submitForm"
              :disabled="disableButton || disabled || successResponse"
            >
              <Transition name="slide-fade"> <span>🎁</span></Transition>
              Отправить!<Transition name="slide-fade">
                <span>🎁</span></Transition
              >
            </button>
            <span
              class="send__button-notify"
              v-if="validateWishLists && !successResponse"
              >Не забудь указать свои пожелания!</span
            >
            <Transition name="slide-fade">
              <span class="send__button-notify" v-if="successResponse"
                >Поздравляем! Ты участвуешь в Тайном Санте 🎅</span
              >
            </Transition>
          </div>
        </form>
      </div>
    </section>
  </main>
</template>

<script setup>
const fullname = ref("");
const email = ref("");
const iWantTags = ref([]);
const iDontWantTags = ref([]);
const config = useRuntimeConfig();

useHead({
  title: "Участвуй в Тайном Санте!",
});

//for inputs
const disabled = ref(false);
const errorMessage = ref("");
const copyLinkSuccess = ref(false);

const successResponse = ref(false);

const copyLink = async () => {
  try {
    const currentUrl = window.location.href; // Текущий URL
    await navigator.clipboard.writeText(currentUrl);
    copyLinkSuccess.value = true;

    setTimeout(() => {
      copyLinkSuccess.value = false;
    }, 2000);
  } catch (err) {
    console.error("Ошибка при копировании ссылки:", err);
  }
};

const updateIWantTags = (tags) => {
  iWantTags.value = tags;
};
const updateIDontWantTags = (tags) => {
  iDontWantTags.value = tags;
};

const postData = computed(() => {
  return {
    full_name: fullname.value,
    email: email.value,
    wishlist: iWantTags.value,
    no_wishlist: iDontWantTags.value,
  };
});

const validateEmail = computed(() => {
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailPattern.test(email.value) && !disabled.value;
});
const validateWishLists = computed(() => {
  return (
    iDontWantTags.value.length === 0 &&
    iWantTags.value.length === 0 &&
    fullname.value.length > 0 &&
    validateEmail.value
  );
});
const disableButton = computed(() => {
  return !validateEmail.value || fullname.value.length === 0;
});

function warnDisabled(errorStatus) {
  disabled.value = true;

  if (errorStatus === 400) {
    errorMessage.value = "Почта уже использовалась для отправки";
  }
  setTimeout(() => {
    disabled.value = false;
  }, 2000);

  setTimeout(() => {
    errorMessage.value = "";
  }, 4000);
}

function warnSuccess() {
  successResponse.value = true;

  setTimeout(() => {
    successResponse.value = false;
  }, 4000);
}
const submitForm = async () => {
  try {
    const data = await $fetch("/api/users", {
      method: "POST",
      baseURL: config.public.apiBase,
      body: postData.value,
    });

    warnSuccess();
  } catch (e) {
    warnDisabled(e.status);
  }
};
</script>
