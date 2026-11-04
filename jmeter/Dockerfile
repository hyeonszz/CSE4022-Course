# JMeter 실행 이미지 (amd64 / arm64 모두 동작)
FROM eclipse-temurin:17-jre-jammy

# 5.4.1 은 log4j-core 2.13.3 번들로 Log4Shell(CVE-2021-44228)에 노출되므로 최신 안정 버전 사용
ENV JMETER_VERSION=5.6.3
ENV JMETER_HOME=/opt/apache-jmeter-${JMETER_VERSION}
ENV PATH=${JMETER_HOME}/bin:$PATH

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# 다운로드 무결성 검증 (공식 sha512 대조)
RUN set -eux; \
    cd /tmp; \
    curl -fsSL -o jmeter.tgz    "https://archive.apache.org/dist/jmeter/binaries/apache-jmeter-${JMETER_VERSION}.tgz"; \
    curl -fsSL -o jmeter.sha512 "https://archive.apache.org/dist/jmeter/binaries/apache-jmeter-${JMETER_VERSION}.tgz.sha512"; \
    EXPECTED="$(tr -d ' \n' < jmeter.sha512 | sed 's/.*://' | grep -oE '[0-9a-fA-F]{128}' | head -1 | tr 'A-Z' 'a-z')"; \
    ACTUAL="$(sha512sum jmeter.tgz | cut -d' ' -f1)"; \
    [ "$EXPECTED" = "$ACTUAL" ] || { echo "checksum mismatch: $ACTUAL != $EXPECTED"; exit 1; }; \
    tar -xzf jmeter.tgz -C /opt/; \
    rm -f jmeter.tgz jmeter.sha512

# 비root 실행 (uid 1000: bind mount 쓰기 권한 문제 방지)
RUN useradd -u 1000 -m -s /bin/bash jmeter && \
    mkdir -p /jmeter && chown -R jmeter:jmeter /jmeter ${JMETER_HOME}

USER jmeter
WORKDIR /jmeter

CMD ["jmeter", "-n"]
