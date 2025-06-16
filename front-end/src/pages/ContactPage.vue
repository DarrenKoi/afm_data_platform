<template>
  <v-container class="pa-6">
    <v-row justify="center">
      <v-col cols="12" lg="10">
        <!-- Header -->
        <div class="text-center mb-8">
          <h1 class="text-h3 font-weight-bold primary--text mb-4">프로젝트 팀</h1>
          <p class="text-h6 text-medium-emphasis">AFM 데이터 플랫폼을 만든 팀을 소개합니다</p>
        </div>

        <!-- Project Leadership -->
        <v-card elevation="3" class="mb-6">
          <v-card-title class="bg-primary">
            <v-icon start>mdi-account-star</v-icon>
            프로젝트 리더십
          </v-card-title>
          <v-card-text class="pa-6">
            <v-row>
              <!-- Frontend Lead -->
              <v-col cols="12" md="6">
                <div class="text-center mb-4">
                  <v-avatar size="80" class="mb-3" color="blue">
                    <v-icon size="40" color="white">mdi-monitor</v-icon>
                  </v-avatar>
                  <h3 class="text-h6 font-weight-bold">최대영</h3>
                  <p class="text-subtitle-1 text-blue mb-2">프론트엔드 리더</p>
                  <p class="text-body-2 text-medium-emphasis">Vue.js & UI/UX 아키텍처 총괄</p>
                </div>
                <v-list dense>
                  <v-list-item>
                    <template #prepend>
                      <v-icon color="blue">mdi-email</v-icon>
                    </template>
                    <v-list-item-title>daeyoung.choi@skhynix.com</v-list-item-title>
                  </v-list-item>
                  <v-list-item>
                    <template #prepend>
                      <v-icon color="blue">mdi-code-tags</v-icon>
                    </template>
                    <v-list-item-title>프론트엔드 개발 & UI/UX 설계</v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-col>

              <!-- Backend Lead -->
              <v-col cols="12" md="6">
                <div class="text-center mb-4">
                  <v-avatar size="80" class="mb-3" color="green">
                    <v-icon size="40" color="white">mdi-server</v-icon>
                  </v-avatar>
                  <h3 class="text-h6 font-weight-bold">유병석</h3>
                  <p class="text-subtitle-1 text-green mb-2">백엔드 리더</p>
                  <p class="text-body-2 text-medium-emphasis">API & 데이터 아키텍처 총괄</p>
                </div>
                <v-list dense>
                  <v-list-item>
                    <template #prepend>
                      <v-icon color="green">mdi-email</v-icon>
                    </template>
                    <v-list-item-title>byungseok.yoo@skhynix.com</v-list-item-title>
                  </v-list-item>
                  <v-list-item>
                    <template #prepend>
                      <v-icon color="green">mdi-database</v-icon>
                    </template>
                    <v-list-item-title>백엔드 개발 & 데이터 처리</v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- Development Teams -->
        <v-card elevation="3" class="mb-6">
          <v-card-title class="bg-secondary">
            <v-icon start>mdi-code-tags</v-icon>
            개발팀
          </v-card-title>
          <v-card-text class="pa-6">
            <v-row>
              <!-- Frontend Team -->
              <v-col cols="12" md="4">
                <div class="mb-4">
                  <h4 class="text-h6 font-weight-bold text-blue mb-3 d-flex align-center">
                    <v-icon color="blue" class="mr-2">mdi-monitor</v-icon>
                    프론트엔드 팀 (4명)
                  </h4>
                  <v-divider color="blue" class="mb-4"></v-divider>
                </div>
                
                <!-- Frontend Team Members -->
                <v-row>
                  <v-col cols="12">
                    <v-card variant="outlined" class="mb-2">
                      <v-card-text class="pa-3">
                        <div class="d-flex align-center">
                          <v-avatar size="32" class="mr-3" color="blue-lighten-1">
                            <v-icon color="white" size="16">mdi-account</v-icon>
                          </v-avatar>
                          <div class="flex-grow-1">
                            <h5 class="text-subtitle-2 font-weight-bold">김민수</h5>
                            <p class="text-caption text-medium-emphasis mb-1">UI/UX 개발자</p>
                            <p class="text-caption">minsu.kim@skhynix.com</p>
                          </div>
                        </div>
                      </v-card-text>
                    </v-card>
                  </v-col>
                  <v-col cols="12">
                    <v-card variant="outlined" class="mb-2">
                      <v-card-text class="pa-3">
                        <div class="d-flex align-center">
                          <v-avatar size="32" class="mr-3" color="blue-lighten-2">
                            <v-icon color="white" size="16">mdi-account</v-icon>
                          </v-avatar>
                          <div class="flex-grow-1">
                            <h5 class="text-subtitle-2 font-weight-bold">박지현</h5>
                            <p class="text-caption text-medium-emphasis mb-1">프론트엔드 개발자</p>
                            <p class="text-caption">jihyun.park@skhynix.com</p>
                          </div>
                        </div>
                      </v-card-text>
                    </v-card>
                  </v-col>
                  <v-col cols="12">
                    <v-card variant="outlined" class="mb-2">
                      <v-card-text class="pa-3">
                        <div class="d-flex align-center">
                          <v-avatar size="32" class="mr-3" color="blue-lighten-3">
                            <v-icon color="white" size="16">mdi-account</v-icon>
                          </v-avatar>
                          <div class="flex-grow-1">
                            <h5 class="text-subtitle-2 font-weight-bold">이상혁</h5>
                            <p class="text-caption text-medium-emphasis mb-1">컴포넌트 개발자</p>
                            <p class="text-caption">sanghyuk.lee@skhynix.com</p>
                          </div>
                        </div>
                      </v-card-text>
                    </v-card>
                  </v-col>
                  <v-col cols="12">
                    <v-card variant="outlined" class="mb-2">
                      <v-card-text class="pa-3">
                        <div class="d-flex align-center">
                          <v-avatar size="32" class="mr-3" color="blue-darken-1">
                            <v-icon color="white" size="16">mdi-account</v-icon>
                          </v-avatar>
                          <div class="flex-grow-1">
                            <h5 class="text-subtitle-2 font-weight-bold">정수빈</h5>
                            <p class="text-caption text-medium-emphasis mb-1">차트 전문가</p>
                            <p class="text-caption">subin.jung@skhynix.com</p>
                          </div>
                        </div>
                      </v-card-text>
                    </v-card>
                  </v-col>
                </v-row>
              </v-col>

              <!-- Backend Team -->
              <v-col cols="12" md="8">
                <div class="mb-4">
                  <h4 class="text-h6 font-weight-bold text-green mb-3 d-flex align-center">
                    <v-icon color="green" class="mr-2">mdi-server</v-icon>
                    백엔드 팀 (8명)
                  </h4>
                  <v-divider color="green" class="mb-4"></v-divider>
                </div>
                
                <!-- Backend Team Members -->
                <v-row>
                  <v-col cols="12" sm="6">
                    <v-card variant="outlined" class="mb-2">
                      <v-card-text class="pa-3">
                        <div class="d-flex align-center">
                          <v-avatar size="32" class="mr-3" color="green-lighten-1">
                            <v-icon color="white" size="16">mdi-account</v-icon>
                          </v-avatar>
                          <div class="flex-grow-1">
                            <h5 class="text-subtitle-2 font-weight-bold">이서준</h5>
                            <p class="text-caption text-medium-emphasis mb-1">API 개발자</p>
                            <p class="text-caption">seojun.lee@skhynix.com</p>
                          </div>
                        </div>
                      </v-card-text>
                    </v-card>
                  </v-col>
                  <v-col cols="12" sm="6">
                    <v-card variant="outlined" class="mb-2">
                      <v-card-text class="pa-3">
                        <div class="d-flex align-center">
                          <v-avatar size="32" class="mr-3" color="green-lighten-2">
                            <v-icon color="white" size="16">mdi-account</v-icon>
                          </v-avatar>
                          <div class="flex-grow-1">
                            <h5 class="text-subtitle-2 font-weight-bold">정유진</h5>
                            <p class="text-caption text-medium-emphasis mb-1">데이터베이스 개발자</p>
                            <p class="text-caption">yujin.jung@skhynix.com</p>
                          </div>
                        </div>
                      </v-card-text>
                    </v-card>
                  </v-col>
                  <v-col cols="12" sm="6">
                    <v-card variant="outlined" class="mb-2">
                      <v-card-text class="pa-3">
                        <div class="d-flex align-center">
                          <v-avatar size="32" class="mr-3" color="green-lighten-3">
                            <v-icon color="white" size="16">mdi-account</v-icon>
                          </v-avatar>
                          <div class="flex-grow-1">
                            <h5 class="text-subtitle-2 font-weight-bold">김태현</h5>
                            <p class="text-caption text-medium-emphasis mb-1">Flask 개발자</p>
                            <p class="text-caption">taehyun.kim@skhynix.com</p>
                          </div>
                        </div>
                      </v-card-text>
                    </v-card>
                  </v-col>
                  <v-col cols="12" sm="6">
                    <v-card variant="outlined" class="mb-2">
                      <v-card-text class="pa-3">
                        <div class="d-flex align-center">
                          <v-avatar size="32" class="mr-3" color="green-darken-1">
                            <v-icon color="white" size="16">mdi-account</v-icon>
                          </v-avatar>
                          <div class="flex-grow-1">
                            <h5 class="text-subtitle-2 font-weight-bold">박성민</h5>
                            <p class="text-caption text-medium-emphasis mb-1">데이터 처리</p>
                            <p class="text-caption">seongmin.park@skhynix.com</p>
                          </div>
                        </div>
                      </v-card-text>
                    </v-card>
                  </v-col>
                  <v-col cols="12" sm="6">
                    <v-card variant="outlined" class="mb-2">
                      <v-card-text class="pa-3">
                        <div class="d-flex align-center">
                          <v-avatar size="32" class="mr-3" color="green">
                            <v-icon color="white" size="16">mdi-account</v-icon>
                          </v-avatar>
                          <div class="flex-grow-1">
                            <h5 class="text-subtitle-2 font-weight-bold">최동욱</h5>
                            <p class="text-caption text-medium-emphasis mb-1">시스템 아키텍트</p>
                            <p class="text-caption">dongwook.choi@skhynix.com</p>
                          </div>
                        </div>
                      </v-card-text>
                    </v-card>
                  </v-col>
                  <v-col cols="12" sm="6">
                    <v-card variant="outlined" class="mb-2">
                      <v-card-text class="pa-3">
                        <div class="d-flex align-center">
                          <v-avatar size="32" class="mr-3" color="green-darken-2">
                            <v-icon color="white" size="16">mdi-account</v-icon>
                          </v-avatar>
                          <div class="flex-grow-1">
                            <h5 class="text-subtitle-2 font-weight-bold">한지우</h5>
                            <p class="text-caption text-medium-emphasis mb-1">스케줄러 개발</p>
                            <p class="text-caption">jiwoo.han@skhynix.com</p>
                          </div>
                        </div>
                      </v-card-text>
                    </v-card>
                  </v-col>
                  <v-col cols="12" sm="6">
                    <v-card variant="outlined" class="mb-2">
                      <v-card-text class="pa-3">
                        <div class="d-flex align-center">
                          <v-avatar size="32" class="mr-3" color="green-darken-3">
                            <v-icon color="white" size="16">mdi-account</v-icon>
                          </v-avatar>
                          <div class="flex-grow-1">
                            <h5 class="text-subtitle-2 font-weight-bold">오준석</h5>
                            <p class="text-caption text-medium-emphasis mb-1">보안 전문가</p>
                            <p class="text-caption">junseok.oh@skhynix.com</p>
                          </div>
                        </div>
                      </v-card-text>
                    </v-card>
                  </v-col>
                  <v-col cols="12" sm="6">
                    <v-card variant="outlined" class="mb-2">
                      <v-card-text class="pa-3">
                        <div class="d-flex align-center">
                          <v-avatar size="32" class="mr-3" color="green-darken-4">
                            <v-icon color="white" size="16">mdi-account</v-icon>
                          </v-avatar>
                          <div class="flex-grow-1">
                            <h5 class="text-subtitle-2 font-weight-bold">신영수</h5>
                            <p class="text-caption text-medium-emphasis mb-1">성능 최적화</p>
                            <p class="text-caption">youngsu.shin@skhynix.com</p>
                          </div>
                        </div>
                      </v-card-text>
                    </v-card>
                  </v-col>
                </v-row>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- Supporters -->
        <v-card elevation="3" class="mb-6">
          <v-card-title class="bg-warning">
            <v-icon start>mdi-hand-heart</v-icon>
            프로젝트 지원팀
          </v-card-title>
          <v-card-text class="pa-6">
            <v-row>
              <!-- Manager -->
              <v-col cols="12" sm="6" md="4" lg="3">
                <div class="text-center mb-4">
                  <v-avatar size="64" class="mb-3" color="orange">
                    <v-icon size="32" color="white">mdi-account-tie</v-icon>
                  </v-avatar>
                  <h4 class="text-h6 font-weight-bold">심규찬</h4>
                  <p class="text-subtitle-2 text-orange mb-2">매니저</p>
                  <p class="text-caption">kyuchan.sim@skhynix.com</p>
                </div>
              </v-col>
              
              <!-- AI/DT Team -->
              <v-col cols="12" sm="6" md="4" lg="3">
                <div class="text-center mb-4">
                  <v-avatar size="64" class="mb-3" color="purple">
                    <v-icon size="32" color="white">mdi-brain</v-icon>
                  </v-avatar>
                  <h4 class="text-h6 font-weight-bold">서종현</h4>
                  <p class="text-subtitle-2 text-purple mb-2">AI/DT 전문가</p>
                  <p class="text-caption">jonghyun.seo@skhynix.com</p>
                </div>
              </v-col>
              
              <!-- Support Member -->
              <v-col cols="12" sm="6" md="4" lg="3">
                <div class="text-center mb-4">
                  <v-avatar size="64" class="mb-3" color="teal">
                    <v-icon size="32" color="white">mdi-account-cog</v-icon>
                  </v-avatar>
                  <h4 class="text-h6 font-weight-bold">이태섭</h4>
                  <p class="text-subtitle-2 text-teal mb-2">기술 지원</p>
                  <p class="text-caption">taeseob.lee@skhynix.com</p>
                </div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>


        <!-- Contact Information -->
        <v-card elevation="3" class="mb-6">
          <v-card-title class="bg-warning">
            <v-icon start>mdi-information</v-icon>
            프로젝트 정보
          </v-card-title>
          <v-card-text class="pa-6">
            <v-row>
              <v-col cols="12" md="6">
                <h4 class="text-h6 font-weight-bold mb-3">일반 문의</h4>
                <v-list dense>
                  <v-list-item>
                    <template #prepend>
                      <v-icon color="warning">mdi-email-multiple</v-icon>
                    </template>
                    <v-list-item-title>afm-platform@skhynix.com</v-list-item-title>
                  </v-list-item>
                  <v-list-item>
                    <template #prepend>
                      <v-icon color="warning">mdi-slack</v-icon>
                    </template>
                    <v-list-item-title>#afm-data-platform</v-list-item-title>
                  </v-list-item>
                  <v-list-item>
                    <template #prepend>
                      <v-icon color="warning">mdi-web</v-icon>
                    </template>
                    <v-list-item-title>내부 위키: wiki.skhynix.com/afm</v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-col>
              <v-col cols="12" md="6">
                <h4 class="text-h6 font-weight-bold mb-3">지원 및 피드백</h4>
                <v-list dense>
                  <v-list-item>
                    <template #prepend>
                      <v-icon color="warning">mdi-bug</v-icon>
                    </template>
                    <v-list-item-title>버그 리포트: GitHub Issues</v-list-item-title>
                  </v-list-item>
                  <v-list-item>
                    <template #prepend>
                      <v-icon color="warning">mdi-lightbulb</v-icon>
                    </template>
                    <v-list-item-title>기능 요청: Slack 채널</v-list-item-title>
                  </v-list-item>
                  <v-list-item>
                    <template #prepend>
                      <v-icon color="warning">mdi-school</v-icon>
                    </template>
                    <v-list-item-title>교육: 월별 세션</v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- External Resources -->
        <v-card elevation="3">
          <v-card-title class="bg-success">
            <v-icon start>mdi-link</v-icon>
            관련 리소스
          </v-card-title>
          <v-card-text class="pa-6">
            <v-row>
              <v-col cols="12" md="6">
                <v-btn 
                  href="http://skewnono.skhynix.com" 
                  target="_blank" 
                  color="primary" 
                  variant="outlined" 
                  class="mb-2 mr-2"
                  block
                >
                  <v-icon start>mdi-chart-line</v-icon>
                  Skewnono 시스템
                  <v-icon end>mdi-open-in-new</v-icon>
                </v-btn>
              </v-col>
              <v-col cols="12" md="6">
                <v-btn 
                  href="http://rnddmi.skhynix.com" 
                  target="_blank" 
                  color="secondary" 
                  variant="outlined" 
                  class="mb-2"
                  block
                >
                  <v-icon start>mdi-database</v-icon>
                  RND DMI 시스템
                  <v-icon end>mdi-open-in-new</v-icon>
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
// Page metadata
defineOptions({
  name: 'ContactPage'
})
</script>