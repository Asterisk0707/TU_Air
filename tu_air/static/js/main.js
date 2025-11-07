// TU_Air/tu_air/static/js/main.js
// (이전 내용 모두 삭제 후, 아래 코드로 전체 덮어쓰기)

document.addEventListener('DOMContentLoaded', function() {
    
    // --- 1. 변수 정의 ---
    const tripTypeButtons = document.querySelectorAll('.trip-type-tabs button');
    const tripTypeInput = document.getElementById('trip_type_input');
    
    // (날짜 관련)
    const datePickerWrapper = document.getElementById('datepicker_wrapper'); // (Wrapper Div)
    const flatpickrInput = document.getElementById('flight_datepicker_input'); // (보여줄 Input)
    const startDateInput = document.getElementById('departure_date'); // (숨겨진 '가는날')
    const endDateInput = document.getElementById('return_date'); // (숨겨진 '오는날')
    
    // (공항 모달 관련)
    const modalOverlay = document.getElementById('airport_modal');
    const depButton = document.getElementById('select_departure_airport');
    const arrButton = document.getElementById('select_arrival_airport');
    const depInput = document.getElementById('departure_airport');
    const arrInput = document.getElementById('arrival_airport');
    
    // (인원/좌석)
    const passengerInput = document.getElementById('passenger_count');
    const classSelect = document.getElementById('seat_class');
    
    const searchForm = document.getElementById('search_form');
    
    let currentInputTarget = null;
    let fp = null; // Flatpickr 인스턴스

    // --- 2. [!!!] Flatpickr (날짜 선택) 생성 함수 (wrap:true) [!!!] ---
    function createDatePicker(isRoundTrip) {
        if (fp) {
            fp.destroy(); // 기존 인스턴스 파괴
        }

        const today = new Date();
        const maxDate = new Date(today.getFullYear() + 1, today.getMonth(), today.getDate() - 1);

        fp = flatpickr(datePickerWrapper, { // (Wrapper Div에 연결)
            
            // [!!! 1. 위치 문제 해결: wrap: true !!!]
            wrap: true, 
            input: flatpickrInput, // (보여줄 input)
            
            mode: isRoundTrip ? "range" : "single",
            dateFormat: "Y-m-d", // (숨겨진 input에 저장할 형식)
            showMonths: 2,
            locale: "ko",
            minDate: "today",
            maxDate: maxDate,
            monthSelectorType: "dropdown", 
            
            onReady: function(selectedDates, dateStr, instance) {
                // '새로고침(Clear)' 버튼 생성
                const clearButton = document.createElement('button');
                clearButton.type = 'button';
                clearButton.className = 'clear-button';
                clearButton.title = '초기화';
                clearButton.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    instance.clear(); 
                    startDateInput.value = '';
                    endDateInput.value = '';
                    flatpickrInput.value = ''; // (보여주는 input 값 비우기)
                    flatpickrInput.placeholder = isRoundTrip ? '가는 날 ~ 오는 날 선택' : '가는 날 선택';
                });
                instance.calendarContainer.appendChild(clearButton);
            },

            onClose: function(selectedDates, dateStr, instance) {
                const currentTripType = tripTypeInput.value;

                if (currentTripType === 'round_trip' && selectedDates.length === 2) {
                    startDateInput.value = instance.formatDate(selectedDates[0], "Y-m-d");
                    endDateInput.value = instance.formatDate(selectedDates[1], "Y-m-d");
                    // (보여주는 input의 값을 업데이트)
                    flatpickrInput.value = `${instance.formatDate(selectedDates[0], "Y.m.d")} - ${instance.formatDate(selectedDates[1], "Y.m.d")}`;
                } else if (currentTripType === 'one_way' && selectedDates.length === 1) {
                    startDateInput.value = instance.formatDate(selectedDates[0], "Y-m-d");
                    endDateInput.value = '';
                    flatpickrInput.value = instance.formatDate(selectedDates[0], "Y.m.d");
                } else if (selectedDates.length === 0) {
                    startDateInput.value = '';
                    endDateInput.value = '';
                    flatpickrInput.value = ''; 
                }
            }
        });
    }

    // --- 3. [!!!] 왕복/편도 탭 이벤트 리스너 (초기화 기능) [!!!] ---
    tripTypeButtons.forEach(button => {
        button.addEventListener('click', () => {
            // 1. 탭 활성화
            tripTypeButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            const type = button.dataset.type;
            tripTypeInput.value = type;
            const isRound = (type === 'round_trip');

            // 2. 날짜 선택기 재생성
            createDatePicker(isRound); 
            
            // 3. [요청] 모든 입력 필드 초기화
            
            // (날짜 초기화)
            const placeholderText = isRound ? '가는 날 ~ 오는 날 선택' : '가는 날 선택';
            flatpickrInput.placeholder = placeholderText; 
            flatpickrInput.value = ''; 
            startDateInput.value = '';
            endDateInput.value = '';
            endDateInput.required = isRound; 

            // (공항 버튼/Input 초기화)
            depInput.value = '';
            arrInput.value = '';
            
            // [!!! 수정: .placeholder <span>을 찾아서 초기화]
            const depNameSpan = depButton.querySelector('.placeholder');
            depNameSpan.style.display = 'inline'; // "출발지 선택" 보이게
            depButton.querySelector('.main-text').textContent = '';
            depButton.querySelector('.sub-text').textContent = '';
            
            const arrNameSpan = arrButton.querySelector('.placeholder');
            arrNameSpan.style.display = 'inline'; // "도착지 선택" 보이게
            arrButton.querySelector('.main-text').textContent = '';
            arrButton.querySelector('.sub-text').textContent = '';
            
            // (인원/좌석 초기화)
            passengerInput.value = '1';
            classSelect.value = 'Economy';
        });
    });

    // --- 4. 검색 버튼 유효성 검사 (이전과 동일) ---
    if (searchForm) {
        searchForm.addEventListener('submit', function(event) {
            if (depInput.value === '') {
                alert('출발지를 선택하세요.');
                event.preventDefault(); return;
            }
            if (arrInput.value === '') {
                alert('도착지를 선택하세요.');
                event.preventDefault(); return;
            }
            if (startDateInput.value === '') {
                alert('가는 날을 선택하세요.');
                event.preventDefault(); return;
            }
            if (tripTypeInput.value === 'round_trip' && endDateInput.value === '') {
                alert('왕복 선택 시 오는 날을 선택해야 합니다.');
                event.preventDefault(); return;
            }
        });
    }

    // --- 5. 공항 선택 모달 로직 (이전과 동일) ---
    depButton.addEventListener('click', () => openModal('departure_airport'));
    arrButton.addEventListener('click', () => openModal('arrival_airport'));
    modalOverlay.querySelector('.modal-close').addEventListener('click', closeModal);
    modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) closeModal();
    });

    function openModal(targetInput) {
        currentInputTarget = targetInput; // 'departure_airport' 또는 'arrival_airport' 저장
        modalOverlay.style.display = 'flex';
        if (!modalOverlay.dataset.loaded) {
            fetchAirportData();
        }
    }
    function closeModal() {
        modalOverlay.style.display = 'none';
    }

    function fetchAirportData() {
        fetch('/get_airports') 
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error("공항 데이터 로드 실패:", data.error);
                    return;
                }
                const tabsContainer = modalOverlay.querySelector('.modal-tabs');
                const listContainer = modalOverlay.querySelector('.modal-list');
                
                // (이하 공항 목록 생성 로직은 동일)
                const koreaTab = document.createElement('button');
                koreaTab.textContent = '대한민국';
                koreaTab.dataset.continent = 'korea';
                koreaTab.classList.add('active');
                tabsContainer.appendChild(koreaTab);
                
                const koreaPane = document.createElement('div');
                koreaPane.id = 'pane-korea';
                koreaPane.classList.add('continent-pane', 'active');
                const koreaGroup = document.createElement('div');
                koreaGroup.classList.add('country-group');
                data.korea.forEach(city => {
                    koreaGroup.appendChild(createCityElement(city));
                });
                koreaPane.appendChild(koreaGroup);
                listContainer.appendChild(koreaPane);

                for (const [continent, countries] of Object.entries(data.continents)) {
                    const tab = document.createElement('button');
                    tab.textContent = continent;
                    tab.dataset.continent = continent;
                    tabsContainer.appendChild(tab);
                    const pane = document.createElement('div');
                    pane.id = `pane-${continent}`;
                    pane.classList.add('continent-pane');
                    for (const [country, cities] of Object.entries(countries)) {
                        const countryGroup = document.createElement('div');
                        countryGroup.classList.add('country-group');
                        const countryName = document.createElement('div');
                        countryName.classList.add('country-name');
                        countryName.textContent = country;
                        countryGroup.appendChild(countryName);
                        cities.forEach(city => {
                            countryGroup.appendChild(createCityElement(city));
                        });
                        pane.appendChild(countryGroup);
                    }
                    listContainer.appendChild(pane);
                }
                
                tabsContainer.querySelectorAll('button').forEach(tab => {
                    tab.addEventListener('click', () => {
                        tabsContainer.querySelector('button.active').classList.remove('active');
                        listContainer.querySelector('.continent-pane.active').classList.remove('active');
                        tab.classList.add('active');
                        document.getElementById(`pane-${tab.dataset.continent}`).classList.add('active');
                    });
                });
                modalOverlay.dataset.loaded = 'true';
            })
            .catch(err => console.error("Fetch 오류:", err));
    }

    function createCityElement(city) {
        const el = document.createElement('div');
        el.classList.add('city-item');
        el.dataset.code = city.Airport_Code;
        el.dataset.name = city.City; 
        el.innerHTML = `<span class="city-name">${city.City}</span><span class="city-code">${city.Airport_Code}</span>`;
        el.addEventListener('click', () => selectAirport(city));
        return el;
    }

    // [!!! 5-1. 공항 선택 함수 수정 (1줄 레이아웃용) !!!]
    function selectAirport(city) {
        // 1. 숨겨진 input에 공항 코드(ICN) 저장
        document.getElementById(currentInputTarget).value = city.Airport_Code; 
        
        // 2. 어떤 버튼을 누른 건지 확인 (출발지 or 도착지)
        const targetButton = (currentInputTarget === 'departure_airport') ? depButton : arrButton;
        
        // 3. 버튼 안의 텍스트 업데이트
        targetButton.querySelector('.placeholder').style.display = 'none'; // "출발지 선택" 숨김
        targetButton.querySelector('.main-text').textContent = city.City;
        targetButton.querySelector('.sub-text').textContent = city.Airport_Code;
        
        closeModal();
    }
    
    // --- 6. 초기 실행 ---
    document.querySelector('.trip-type-tabs button[data-type="round_trip"]').click();
});