<template>
  <div class="container">
    <div class="settings__section settings__section-profile-image">
      <div class="profile__image-container">
        <profile-image-component width="100px" height="100px" :profile="profile"></profile-image-component>
        <form class="form__profile-image" @change="openEditProfileImage" @submit.prevent="() => {}" ref="profileImageForm">
          <input type="file" accept="image/png,image/jpeg" class="button-upload" ref="profileImageInput">
          <i class="button__edit button__edit-profile-image fas fa-pen"></i>
        </form>
      </div>
      <div>
        <button class="button button__logout" @click="logout">로그아웃</button>
      </div>
    </div>

    <div class="settings__section " v-if="userinfo.email">
      <div class="label">이메일</div>
      <div class="value">{{ userinfo.email }}</div>
    </div>
    <div class="settings__section " v-else>
      <div class="label">아이디</div>
      <div class="value">{{ username }}</div>
    </div>

    <div class="settings__section settings__nickname">
      <div class="label">유저네임</div>
      <div class="value" v-if="!isEditing.nickname">
        <span>{{ nickname || '이름이 설정되어 있지 않습니다.' }}</span>
        <i class="button__edit button__edit-nickname fas fa-pen" @click="openChangeNickname"></i>
      </div>
      <div class="value" v-if="isEditing.nickname">
        <form class="form__nickname" @submit.prevent="changeNickname">
          <div class="wrapper">
            <input type="text" class="form__input"
                   ref="inputNickname"
                   v-model.trim="newNickname"
                   :placeholder="nickname || '이름이 설정되어 있지 않습니다.'">
            <div class="form__error" v-if="formErrors.nickname">{{ formErrors.nickname }}</div>
          </div>
          <div class="wrapper">
            <button type="button" class="form__button" @click="cancelChangeNickname">취소</button>
            <button type="submit" class="form__button">확인</button>
          </div>
        </form>
      </div>
    </div>

    <div class="settings__section settings__recommended_code">
      <div class="label">나의 추천인 코드</div>
      <div class="value" @click="copyCode">
        <input type="text"
               class="input__copy-permalink"
               ref="permalink"
               readonly
               :value="userinfo.recommended_code">
        <span class="settings__section-copy">&nbsp;COPY&nbsp;</span>
      </div>
    </div>

    <div class="settings__section " v-if="!steemUsername">
      <div class="label">스팀잇 아이디 연결</div>

      <div class="value" v-if="!userinfo.social_auth.steemconnect">
        <a :href="steemLoginUrl" class="login-form__login-button login-form__login-steemit">Login with SteemConnect</a>
      </div>
      <div class="value" v-else>
        <div class="loading__steemconnect" v-if="!isSteemConnectLoaded"><loading-spinner></loading-spinner></div>
        <div v-else>
          <div class="login-form__login-button login-form__login-steemit active" v-if="isAvailableSteemConnect">
            <i class="fas fa-check steem__check"></i>
            {{ userinfo.social_auth.steemconnect.username }} 계정으로 연결함
          </div>
          <div v-else>
            <p>연동이 만료되었습니다. 다시 연동하세요.</p>
            <a :href="steemLoginUrl" class="login-form__login-button login-form__login-steemit">Login with SteemConnect</a>
          </div>
        </div>
      </div>
    </div>
    <div class="settings__section " v-else>
      <div class="label">스팀잇 아이디</div>
      <div class="value">{{ steemUsername }}</div>
    </div>

    <div class="settings__section ">
      <div class="label">알림 설정</div>
      <form
        class="form__notification-settings"
        @submit.prevent="updateNotificationSettings"
        @change.prevent="updateNotificationSettings">
        <ul class="value">
          <li>
            <label for="liked-my-post">좋아요</label>
            <input type="checkbox" id="liked-my-post" v-model="notificationSettings.liked_my_post">
          </li>
          <li>
            <label for="new-comment-user-posted">댓글</label>
            <input type="checkbox" id="new-comment-user-posted" v-model="notificationSettings.new_comment_user_posted">
          </li>
          <li>
            <label for="my-new-follower">새 팔로워</label>
            <input type="checkbox" id="my-new-follower" v-model="notificationSettings.my_new_follower">
          </li>
          <li>
            <label for="following-new-post">새 게시물</label>
            <input type="checkbox" id="following-new-post" v-model="notificationSettings.following_new_post">
          </li>
        </ul>
      </form>
    </div>

    <div :class="['section__edit-profile-image', {active: isEditProfileImageSection}]">
      <img class="image"
           :src="editImage"
           ref="profileImageSrc">
      <div class="section__footer">
        <button class="button" @click="cancelEditProfileImage">취소</button>
        <button class="button" @click="submitProfileImage">선택</button>
      </div>
    </div>

  </div>
</template>

<script lang="ts">
import Settings from './scripts/settings';
export default Settings;
</script>

<style lang="scss" scoped>
@import '~@/assets/styles/Settings.scss';
</style>
