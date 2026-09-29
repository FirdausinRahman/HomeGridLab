import streamlit as st
import folium

from streamlit_folium import st_folium

from prediction import predict_land_price
from accessibility import get_accessibility_profile


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="HomeGridLab",
    page_icon="🏠",
    layout="centered"
)


# ============================================================
# DEFAULT LOCATION
# ============================================================

DEFAULT_LAT = -6.9053734202498
DEFAULT_LON = 107.67250589972


# ============================================================
# AMENITY INFORMATION
# ============================================================

AMENITY_INFO = {

    "Leisure": {
        "icon": "🏖️",
    },

    "Education": {
        "icon": "🎓",
    },

    "Finance": {
        "icon": "💰",
    },

    "Culinary": {
        "icon": "🍜",
    },

    "Government Office": {
        "icon": "🏛️",
    },

    "Health": {
        "icon": "🏥",
    },

    "Worshiping Place": {
        "icon": "🕌",
    },

    "Retail / Store": {
        "icon": "🛍️",
    },

    "Sport & Park": {
        "icon": "⚽",
    },

    "Tourism Accommodation": {
        "icon": "🏨",
    },
}


# ============================================================
# SESSION STATE
# ============================================================

if "selected_lat" not in st.session_state:
    st.session_state.selected_lat = DEFAULT_LAT

if "selected_lon" not in st.session_state:
    st.session_state.selected_lon = DEFAULT_LON


# ============================================================
# GLOBAL STYLE
# ============================================================

st.html(
    """
    <style>

    /* -------------------------------------------------------
       GENERAL
    ------------------------------------------------------- */

    .block-container {
        max-width: 1050px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }


    /* -------------------------------------------------------
       LOCATION PROFILE INTRO
    ------------------------------------------------------- */

    .profile-intro {
        margin-top: 28px;
        margin-bottom: 18px;
    }

    .eyebrow {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.12em;
        color: #64748b;
        margin-bottom: 6px;
    }

    .profile-title {
        font-size: 30px;
        font-weight: 750;
        line-height: 1.1;
        color: #0f172a;
        margin-bottom: 7px;
    }

    .profile-description {
        font-size: 15px;
        line-height: 1.55;
        color: #64748b;
        max-width: 650px;
    }


    /* -------------------------------------------------------
       SELECTED LOCATION
    ------------------------------------------------------- */

    .location-card {
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 18px 20px;
        background: #ffffff;
        margin-top: 8px;
        margin-bottom: 18px;
    }

    .location-card-title {
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.08em;
        color: #64748b;
        margin-bottom: 6px;
    }

    .location-coordinate {
        font-size: 16px;
        font-weight: 650;
        color: #0f172a;
    }

    .location-helper {
        font-size: 12px;
        color: #94a3b8;
        margin-top: 4px;
    }


    /* -------------------------------------------------------
       DONUT
    ------------------------------------------------------- */

    .donut-wrap {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 12px 0 16px 0;
    }

    .donut {
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .donut.outer {
        width: 158px;
        height: 158px;
        padding: 11px;
    }

    .donut.inner {
        width: 112px;
        height: 112px;
        padding: 8px;
    }

    .donut-center {
        width: 94px;
        height: 94px;
        background: white;
        border-radius: 50%;

        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;

        text-align: center;
    }

    .donut-number {
        font-size: 27px;
        font-weight: 750;
        line-height: 1;
        color: #0f172a;
    }

    .donut-label {
        margin-top: 6px;
        font-size: 10px;
        line-height: 1.2;
        color: #64748b;
    }


    /* -------------------------------------------------------
       HERO CARD
    ------------------------------------------------------- */

    .hero-card {
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 20px;
        background: #ffffff;
        height: 100%;
        box-shadow: 0 3px 14px rgba(15, 23, 42, 0.04);
    }

    .hero-icon {
        font-size: 27px;
        margin-bottom: 5px;
    }

    .hero-title {
        font-size: 19px;
        font-weight: 750;
        color: #0f172a;
    }

    .hero-description {
        font-size: 12px;
        color: #64748b;
        margin-top: 2px;
    }

    .hero-metrics {
        display: flex;
        justify-content: center;
        gap: 22px;
        margin-top: 3px;
    }

    .hero-metric {
        text-align: center;
    }

    .hero-metric-value {
        font-size: 14px;
        font-weight: 700;
        color: #0f172a;
    }

    .hero-metric-label {
        font-size: 10px;
        color: #94a3b8;
        margin-top: 2px;
    }


    /* -------------------------------------------------------
       SECTION
    ------------------------------------------------------- */

    .section-title {
        font-size: 18px;
        font-weight: 750;
        color: #0f172a;
        margin-top: 26px;
        margin-bottom: 4px;
    }

    .section-description {
        font-size: 12px;
        color: #64748b;
        margin-bottom: 14px;
    }


    /* -------------------------------------------------------
       MATRIX
    ------------------------------------------------------- */

    .matrix-header {
        font-size: 10px;
        font-weight: 700;
        color: #94a3b8;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        padding-bottom: 6px;
    }

    .matrix-name {
        font-size: 13px;
        color: #334155;
        font-weight: 550;
        white-space: nowrap;
    }

    .signal {
        display: flex;
        align-items: flex-end;
        gap: 3px;
        height: 22px;
    }

    .signal-bar {
        width: 6px;
        border-radius: 2px;
        background: #e2e8f0;
    }

    .signal-bar:nth-child(1) {
        height: 7px;
    }

    .signal-bar:nth-child(2) {
        height: 10px;
    }

    .signal-bar:nth-child(3) {
        height: 13px;
    }

    .signal-bar:nth-child(4) {
        height: 17px;
    }

    .signal-bar:nth-child(5) {
        height: 21px;
    }

    .signal-blue {
        background: #2563eb;
    }

    .signal-green {
        background: #22c55e;
    }

    .signal-yellow {
        background: #eab308;
    }

    .signal-orange {
        background: #f97316;
    }

    .signal-red {
        background: #ef4444;
    }


    /* -------------------------------------------------------
       2D PROFILE CHART
    ------------------------------------------------------- */

    .profile-chart {
        position: relative;
        width: 100%;
        height: 390px;
        margin-top: 15px;
    }

    .chart-area {
        position: absolute;

        left: 58px;
        right: 24px;
        top: 20px;
        bottom: 55px;

        border-left: 1px solid #cbd5e1;
        border-bottom: 1px solid #cbd5e1;

        background:
            linear-gradient(
                to right,
                rgba(148, 163, 184, 0.13) 1px,
                transparent 1px
            ),
            linear-gradient(
                to bottom,
                rgba(148, 163, 184, 0.13) 1px,
                transparent 1px
            );

        background-size:
            25% 25%;

        overflow: visible;
    }

    .grid-line {
        position: absolute;
        background: #e2e8f0;
    }

    .grid-line.horizontal {
        left: 0;
        right: 0;
        height: 1px;
    }

    .grid-line.vertical {
        top: 0;
        bottom: 0;
        width: 1px;
    }

    .h25 {
        bottom: 25%;
    }

    .h50 {
        bottom: 50%;
    }

    .h75 {
        bottom: 75%;
    }

    .v25 {
        left: 25%;
    }

    .v50 {
        left: 50%;
    }

    .v75 {
        left: 75%;
    }

    .profile-point {
        position: absolute;

        transform: translate(-50%, 50%);

        width: 36px;
        height: 36px;

        border-radius: 50%;

        background: white;

        border: 1px solid #e2e8f0;

        display: flex;
        align-items: center;
        justify-content: center;

        font-size: 20px;

        box-shadow:
            0 3px 10px rgba(15, 23, 42, 0.14);

        cursor: pointer;

        z-index: 5;

        transition:
            transform 0.15s ease,
            box-shadow 0.15s ease;
    }

    .profile-point:hover {
        transform:
            translate(-50%, 50%)
            scale(1.25);

        box-shadow:
            0 6px 18px rgba(15, 23, 42, 0.18);

        z-index: 20;
    }

    .point-tooltip {
        position: absolute;

        bottom: 42px;
        left: 50%;

        transform: translateX(-50%);

        background: #0f172a;
        color: white;

        padding: 7px 9px;

        border-radius: 7px;

        font-size: 10px;
        line-height: 1.4;

        white-space: nowrap;

        opacity: 0;
        pointer-events: none;

        transition: opacity 0.12s ease;

        z-index: 30;
    }

    .profile-point:hover .point-tooltip {
        opacity: 1;
    }

    .axis-x-label {
        position: absolute;

        bottom: 12px;
        left: 50%;

        transform: translateX(-50%);

        font-size: 12px;
        font-weight: 650;

        color: #64748b;
    }

    .axis-y-label {
        position: absolute;

        left: 12px;
        top: 50%;

        transform:
            translate(-50%, -50%)
            rotate(-90deg);

        font-size: 12px;
        font-weight: 650;

        color: #64748b;
    }

    .axis-value {
        position: absolute;
        font-size: 9px;
        color: #94a3b8;
    }

    .axis-value-y-0 {
        left: 38px;
        bottom: 49px;
    }

    .axis-value-y-25 {
        left: 31px;
        bottom: calc(25% + 44px);
    }

    .axis-value-y-50 {
        left: 31px;
        bottom: calc(50% + 44px);
    }

    .axis-value-y-75 {
        left: 31px;
        bottom: calc(75% + 44px);
    }

    .axis-value-y-100 {
        left: 25px;
        top: 13px;
    }

    .axis-value-x-0 {
        left: 53px;
        bottom: 39px;
    }

    .axis-value-x-25 {
        left: calc(25% + 49px);
        bottom: 39px;
    }

    .axis-value-x-50 {
        left: calc(50% + 49px);
        bottom: 39px;
    }

    .axis-value-x-75 {
        left: calc(75% + 49px);
        bottom: 39px;
    }

    .axis-value-x-100 {
        right: 17px;
        bottom: 39px;
    }


    /* -------------------------------------------------------
       LEGEND
    ------------------------------------------------------- */

    .chart-legend {
        display: flex;
        justify-content: center;
        gap: 18px;

        margin-top: 8px;

        font-size: 11px;
        color: #64748b;
    }

    .legend-item {
        display: flex;
        align-items: center;
        gap: 5px;
    }

    .legend-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
    }

    .legend-choice {
        background: #2563eb;
    }

    .legend-access {
        background: #22c55e;
    }


    /* -------------------------------------------------------
       MODAL
    ------------------------------------------------------- */

    div[data-testid="stDialog"] {
        border-radius: 22px;
    }

    </style>
    """
)


# ============================================================
# HELPER — SIGNAL COLOR
# ============================================================

def signal_color(level):

    if level == 5:
        return "signal-blue"

    if level == 4:
        return "signal-green"

    if level == 3:
        return "signal-yellow"

    if level == 2:
        return "signal-orange"

    return "signal-red"


# ============================================================
# HELPER — SIGNAL HTML
# ============================================================

def signal_html(level):

    bars = ""

    for i in range(1, 6):

        if i <= level:
            color_class = signal_color(level)
        else:
            color_class = ""

        bars += f"""
        <div class="signal-bar {color_class}"></div>
        """

    return f"""
    <div class="signal">
        {bars}
    </div>
    """


# ============================================================
# HELPER — DONUT HTML
# ============================================================

def donut_html(
    choice,
    access,
    overall
):

    choice = max(
        0,
        min(100, float(choice))
    )

    access = max(
        0,
        min(100, float(access))
    )

    return f"""
    <div class="donut-wrap">

        <div
            class="donut outer"
            style="
                background:
                conic-gradient(
                    #2563eb {choice}%,
                    #e5e7eb 0
                );
            "
        >

            <div
                class="donut inner"
                style="
                    background:
                    conic-gradient(
                        #22c55e {access}%,
                        #e5e7eb 0
                    );
                "
            >

                <div class="donut-center">

                    <div class="donut-number">
                        {overall:.0f}
                    </div>

                    <div class="donut-label">
                        Overall Access
                    </div>

                </div>

            </div>

        </div>

    </div>
    """


# ============================================================
# HELPER — 2D PROFILE CHART
# ============================================================

def profile_chart_html(profile):

    points = ""

    for category, data in profile.items():

        if data is None:
            continue

        accessibility = float(
            data["accessibility"]
        )

        choice_variety = float(
            data["choice_variety"]
        )

        icon = AMENITY_INFO.get(
            category,
            {}
        ).get(
            "icon",
            "•"
        )

        # Prevent icon from touching chart boundary
        x = max(
            2,
            min(98, accessibility)
        )

        y = max(
            2,
            min(98, choice_variety)
        )

        points += f"""

        <div
            class="profile-point"
            style="
                left: {x}%;
                bottom: {y}%;
            "
        >

            {icon}

            <div class="point-tooltip">

                <strong>{category}</strong><br>

                Accessibility:
                {accessibility:.1f}<br>

                Choice Variety:
                {choice_variety:.1f}

            </div>

        </div>

        """

    return f"""
    <div class="profile-chart">

        <div class="axis-y-label">
            Choice Variety
        </div>

        <div class="chart-area">

            <div class="grid-line horizontal h25"></div>
            <div class="grid-line horizontal h50"></div>
            <div class="grid-line horizontal h75"></div>

            <div class="grid-line vertical v25"></div>
            <div class="grid-line vertical v50"></div>
            <div class="grid-line vertical v75"></div>

            {points}

        </div>


        <div class="axis-value axis-value-y-0">
            0
        </div>

        <div class="axis-value axis-value-y-25">
            25
        </div>

        <div class="axis-value axis-value-y-50">
            50
        </div>

        <div class="axis-value axis-value-y-75">
            75
        </div>

        <div class="axis-value axis-value-y-100">
            100
        </div>


        <div class="axis-value axis-value-x-0">
            0
        </div>

        <div class="axis-value axis-value-x-25">
            25
        </div>

        <div class="axis-value axis-value-x-50">
            50
        </div>

        <div class="axis-value axis-value-x-75">
            75
        </div>

        <div class="axis-value axis-value-x-100">
            100
        </div>


        <div class="axis-x-label">
            Accessibility
        </div>

    </div>
    """


# ============================================================
# LOCATION PROFILE DIALOG
# ============================================================

@st.dialog(
    "Location Profile",
    width="large"
)
def location_profile_dialog():

    latitude = st.session_state.selected_lat
    longitude = st.session_state.selected_lon

    profile = get_accessibility_profile(
        latitude=latitude,
        longitude=longitude
    )

    if profile is None:

        st.error(
            "Location profile could not be generated."
        )

        return


    # ========================================================
    # INTRO
    # ========================================================

    st.html(
        """
        <div style="
            margin-bottom: 20px;
        ">

            <div class="eyebrow">
                AMENITIES & FACILITIES
            </div>

            <div class="profile-title">
                What's around this location?
            </div>

            <div class="profile-description">
                Explore accessibility and choice variety
                across major amenity categories.
            </div>

        </div>
        """
    )


    # ========================================================
    # HERO CARDS
    # ========================================================

    hero_left, hero_right = st.columns(
        2,
        gap="medium"
    )


    # --------------------------------------------------------
    # EDUCATION
    # --------------------------------------------------------

    education = profile.get(
        "Education"
    )

    with hero_left:

        if education is not None:

            st.html(
                f"""
                <div class="hero-card">

                    <div class="hero-icon">
                        🎓
                    </div>

                    <div class="hero-title">
                        Education
                    </div>

                    <div class="hero-description">
                        Access and variety of education
                        facilities.
                    </div>

                    {donut_html(
                        education["choice_variety"],
                        education["accessibility"],
                        education["overall"]
                    )}

                    <div class="hero-metrics">

                        <div class="hero-metric">

                            <div class="hero-metric-value">
                                {education["accessibility"]:.1f}
                            </div>

                            <div class="hero-metric-label">
                                Accessibility
                            </div>

                        </div>

                        <div class="hero-metric">

                            <div class="hero-metric-value">
                                {education["choice_variety"]:.1f}
                            </div>

                            <div class="hero-metric-label">
                                Choice Variety
                            </div>

                        </div>

                    </div>

                </div>
                """
            )

        else:

            st.warning(
                "Education data unavailable."
            )


    # --------------------------------------------------------
    # HEALTH
    # --------------------------------------------------------

    health = profile.get(
        "Health"
    )

    with hero_right:

        if health is not None:

            st.html(
                f"""
                <div class="hero-card">

                    <div class="hero-icon">
                        🏥
                    </div>

                    <div class="hero-title">
                        Health
                    </div>

                    <div class="hero-description">
                        Access and variety of health
                        facilities.
                    </div>

                    {donut_html(
                        health["choice_variety"],
                        health["accessibility"],
                        health["overall"]
                    )}

                    <div class="hero-metrics">

                        <div class="hero-metric">

                            <div class="hero-metric-value">
                                {health["accessibility"]:.1f}
                            </div>

                            <div class="hero-metric-label">
                                Accessibility
                            </div>

                        </div>

                        <div class="hero-metric">

                            <div class="hero-metric-value">
                                {health["choice_variety"]:.1f}
                            </div>

                            <div class="hero-metric-label">
                                Choice Variety
                            </div>

                        </div>

                    </div>

                </div>
                """
            )

        else:

            st.warning(
                "Health data unavailable."
            )


    # ========================================================
    # AMENITY MATRIX
    # ========================================================

    st.html(
        """
        <div class="section-title">
            Amenity Profile
        </div>

        <div class="section-description">
            A quick comparison of accessibility and choice variety.
        </div>
        """
    )


    # Header
    header_name, header_access, header_choice = st.columns(
        [2.4, 1, 1]
    )

    with header_name:

        st.html(
            """
            <div class="matrix-header">
                Amenity
            </div>
            """
        )

    with header_access:

        st.html(
            """
            <div class="matrix-header">
                Access
            </div>
            """
        )

    with header_choice:

        st.html(
            """
            <div class="matrix-header">
                Variety
            </div>
            """
        )


    # Rows
    for category, data in profile.items():

        if data is None:
            continue

        icon = AMENITY_INFO.get(
            category,
            {}
        ).get(
            "icon",
            "•"
        )

        name_col, access_col, choice_col = st.columns(
            [2.4, 1, 1]
        )

        with name_col:

            st.html(
                f"""
                <div class="matrix-name">
                    {icon}
                    &nbsp;
                    {category}
                </div>
                """
            )

        with access_col:

            st.html(
                signal_html(
                    data["accessibility_level"]
                )
            )

        with choice_col:

            st.html(
                signal_html(
                    data["choice_level"]
                )
            )


    # ========================================================
    # 2D PROFILE
    # ========================================================

    st.html(
        """
        <div class="section-title">
            Location Amenity Profile
        </div>

        <div class="section-description">
            Each icon represents an amenity category.
            Horizontal position shows accessibility,
            while vertical position shows choice variety.
        </div>
        """
    )


    st.html(
        profile_chart_html(
            profile
        )
    )


    # ========================================================
    # LEGEND
    # ========================================================

    st.html(
        """
        <div class="chart-legend">

            <div class="legend-item">
                <div class="legend-dot legend-access"></div>
                Accessibility
            </div>

            <div class="legend-item">
                <div class="legend-dot legend-choice"></div>
                Choice Variety
            </div>

        </div>
        """
    )


# ============================================================
# PAGE HEADER
# ============================================================

st.html(
    """
    <div style="
        margin-bottom: 18px;
    ">

        <div style="
            font-size: 12px;
            font-weight: 750;
            letter-spacing: 0.12em;
            color: #64748b;
        ">
            HOMEGRIDLAB
        </div>

        <div style="
            font-size: 30px;
            font-weight: 800;
            color: #0f172a;
            margin-top: 3px;
        ">
            Property Intelligence
        </div>

        <div style="
            font-size: 14px;
            color: #64748b;
            margin-top: 4px;
        ">
            Explore property value and location characteristics.
        </div>

    </div>
    """
)


# ============================================================
# MAP
# ============================================================

latitude = st.session_state.selected_lat
longitude = st.session_state.selected_lon


m = folium.Map(
    location=[
        latitude,
        longitude
    ],
    zoom_start=14,
    control_scale=True
)


# Selected location marker
folium.Marker(
    location=[
        latitude,
        longitude
    ],
    tooltip="Selected location",
    icon=folium.Icon(
        color="blue",
        icon="home",
        prefix="fa"
    )
).add_to(m)


map_data = st_folium(
    m,
    width=None,
    height=480,
    returned_objects=[
        "last_clicked"
    ]
)


# ============================================================
# MAP CLICK
# ============================================================

if map_data:

    clicked = map_data.get(
        "last_clicked"
    )

    if clicked:

        clicked_lat = clicked["lat"]
        clicked_lon = clicked["lng"]

        if (
            clicked_lat
            != st.session_state.selected_lat
            or
            clicked_lon
            != st.session_state.selected_lon
        ):

            st.session_state.selected_lat = clicked_lat
            st.session_state.selected_lon = clicked_lon

            st.rerun()


# ============================================================
# SELECTED LOCATION
# ============================================================

st.html(
    f"""
    <div class="location-card">

        <div class="location-card-title">
            SELECTED LOCATION
        </div>

        <div class="location-coordinate">
            {latitude:.6f}, {longitude:.6f}
        </div>

        <div class="location-helper">
            Click anywhere on the map to change location.
        </div>

    </div>
    """
)


# ============================================================
# LOCATION ACTIONS
# ============================================================

col1, col2 = st.columns(
    [1, 1]
)


with col1:

    if st.button(
        "Explore amenities & facilities →",
        use_container_width=True
    ):

        location_profile_dialog()


with col2:

    if st.button(
        "Reset location",
        use_container_width=True
    ):

        st.session_state.selected_lat = DEFAULT_LAT
        st.session_state.selected_lon = DEFAULT_LON

        st.rerun()


# ============================================================
# LAND PRICE ESTIMATION
# ============================================================

st.divider()


st.html(
    """
    <div class="section-title">
        Property Value Estimate
    </div>

    <div class="section-description">
        Estimated land value based on the selected location
        and the HomeGridLab prediction model.
    </div>
    """
)


if st.button(
    "Estimate property value",
    use_container_width=True
):

    predicted_price = predict_land_price(

        latitude=latitude,

        longitude=longitude,

        # ----------------------------------------------------
        # Hidden categorical defaults
        # ----------------------------------------------------

        bentuk_tapak="Persegi",

        orientasi="Utara",

        kondisi_wilayah_sekitar="Komersial"
    )


    if predicted_price is None:

        st.error(
            "Property value could not be estimated "
            "for this location."
        )

    else:

        st.success(
            f"Estimated land value: "
            f"Rp {predicted_price:,.0f} / m²"
        )
